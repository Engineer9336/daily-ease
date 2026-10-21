from sqlalchemy import select, or_
from .db import get_session, User, WorkerProfile, ServiceRequest, ActivityLog

STATUSES = {"Pending", "Accepted", "Rejected", "In Progress", "Completed", "Cancelled"}
TRANSITIONS = {"Pending": {"Accepted", "Rejected", "Cancelled"}, "Accepted": {"In Progress", "Cancelled"}, "In Progress": {"Completed"}, "Rejected": set(), "Completed": set(), "Cancelled": set()}

def search_workers(query="", category="All categories", locality=""):
    with get_session() as s:
        stmt = select(WorkerProfile, User).join(User).where(WorkerProfile.is_active.is_(True), User.active.is_(True))
        if category and category != "All categories": stmt = stmt.where(WorkerProfile.category == category)
        if locality.strip(): stmt = stmt.where(User.locality.ilike(f"%{locality.strip()}%"))
        if query.strip():
            q = f"%{query.strip()}%"
            stmt = stmt.where(or_(WorkerProfile.category.ilike(q), WorkerProfile.skills.ilike(q), WorkerProfile.bio.ilike(q), User.name.ilike(q)))
        return [{"profile_id": p.id, "user_id": u.id, "name": u.name, "locality": u.locality, "category": p.category, "skills": p.skills, "bio": p.bio, "experience_years": p.experience_years, "price": p.price, "availability": p.availability, "languages": p.languages, "verification_status": p.verification_status, "is_demo": p.is_demo, "photo_path": p.photo_path} for p,u in s.execute(stmt).all()]

def update_worker_profile(user_id, category, skills, bio, experience_years, price, availability, languages):
    if not category.strip() or not skills.strip(): raise ValueError("Category and skills are required.")
    if not 0 <= int(experience_years) <= 80: raise ValueError("Experience must be between 0 and 80 years.")
    with get_session() as s:
        user = s.get(User, user_id)
        if not user or user.role != "worker": raise PermissionError("Only workers can edit worker profiles.")
        p = user.worker_profile
        if not p: p = WorkerProfile(user_id=user_id); s.add(p)
        p.category, p.skills, p.bio = category.strip(), skills.strip(), bio.strip()
        p.experience_years, p.price, p.availability, p.languages = int(experience_years), price.strip(), availability.strip(), languages.strip()
        p.is_demo = False
        s.add(ActivityLog(actor_id=user_id, action="worker_profile_updated")); s.commit()

def create_request(customer_id, worker_id, description, location, preferred_time="Flexible"):
    description, location = description.strip(), location.strip()
    if len(description) < 5: raise ValueError("Please describe the work in at least 5 characters.")
    if not location: raise ValueError("Service location is required.")
    with get_session() as s:
        customer, worker = s.get(User, customer_id), s.get(User, worker_id)
        if not customer or customer.role != "customer": raise PermissionError("Only a customer account can submit a request.")
        if not worker or worker.role != "worker" or not worker.active or not worker.worker_profile or not worker.worker_profile.is_active: raise ValueError("This worker is unavailable.")
        r = ServiceRequest(customer_id=customer_id, worker_id=worker_id, description=description, service_location=location, preferred_time=preferred_time.strip() or "Flexible")
        s.add(r); s.flush(); s.add(ActivityLog(actor_id=customer_id, action="service_request_created", details=f"request_id={r.id}")); s.commit(); return r.id

def list_requests(user_id, role):
    with get_session() as s:
        if role == "admin": rows = s.scalars(select(ServiceRequest).order_by(ServiceRequest.created_at.desc())).all()
        elif role == "customer": rows = s.scalars(select(ServiceRequest).where(ServiceRequest.customer_id == user_id).order_by(ServiceRequest.created_at.desc())).all()
        elif role == "worker": rows = s.scalars(select(ServiceRequest).where(ServiceRequest.worker_id == user_id).order_by(ServiceRequest.created_at.desc())).all()
        else: raise PermissionError("Unknown role.")
        result=[]
        for r in rows:
            c, w = s.get(User, r.customer_id), s.get(User, r.worker_id)
            result.append({"id":r.id,"customer_id":r.customer_id,"customer_name":c.name if c else "Unknown","worker_id":r.worker_id,"worker_name":w.name if w else "Unknown","description":r.description,"location":r.service_location,"preferred_time":r.preferred_time,"status":r.status,"created_at":str(r.created_at)})
        return result

def change_request_status(request_id, actor_id, actor_role, new_status):
    if new_status not in STATUSES: raise ValueError("Invalid request status.")
    with get_session() as s:
        r = s.get(ServiceRequest, request_id)
        if not r: raise ValueError("Service request not found.")
        allowed = (actor_role == "customer" and r.customer_id == actor_id and new_status == "Cancelled") or (actor_role == "worker" and r.worker_id == actor_id and new_status in TRANSITIONS[r.status]) or (actor_role == "admin")
        if not allowed: raise PermissionError("You do not have permission to change this request.")
        if actor_role != "admin" and new_status not in TRANSITIONS[r.status]: raise ValueError(f"Cannot change status from {r.status} to {new_status}.")
        r.status = new_status; s.add(ActivityLog(actor_id=actor_id, action="request_status_changed", details=f"request_id={request_id};status={new_status}")); s.commit()

def admin_stats():
    with get_session() as s:
        return {"customers":len(s.scalars(select(User).where(User.role=="customer")).all()),"workers":len(s.scalars(select(User).where(User.role=="worker")).all()),"requests":len(s.scalars(select(ServiceRequest)).all()),"pending":len(s.scalars(select(ServiceRequest).where(ServiceRequest.status=="Pending")).all())}

def update_worker_photo(user_id, path):
    with get_session() as s:
        u=s.get(User,user_id)
        if not u or u.role != "worker" or not u.worker_profile: raise PermissionError("Worker profile not found.")
        u.worker_profile.photo_path=path; u.worker_profile.is_demo=False; s.commit()
