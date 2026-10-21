import os
from pathlib import Path
import streamlit as st
from PIL import Image, UnidentifiedImageError
from daily_ease.config import UPLOAD_DIR, MAX_IMAGE_BYTES
from daily_ease.db import init_db, seed_demo_data, get_session, User, WorkerProfile, ServiceRequest
from daily_ease.auth import register_user, authenticate
from daily_ease.services import search_workers, update_worker_profile, create_request, list_requests, change_request_status, admin_stats, update_worker_photo
from daily_ease.i18n import t, TRANSLATIONS, missing_keys
from daily_ease.assistant import answer
from sqlalchemy import select

st.set_page_config(page_title="Daily Ease", page_icon="🏡", layout="wide", initial_sidebar_state="expanded")
init_db(); seed_demo_data()
if "language" not in st.session_state: st.session_state.language="en"
if "user" not in st.session_state: st.session_state.user=None
if "page" not in st.session_state: st.session_state.page="home"
lang=st.session_state.language

st.markdown("""<style>
:root { --de-green:#217a4b; --de-light:#f5f8f4; }
.block-container{padding-top:1.4rem;max-width:1200px}
[data-testid="stAppViewContainer"]{background:var(--de-light)}
.de-hero{background:#e7f2e8;border:1px solid #d4e7d6;border-radius:18px;padding:28px 30px;margin:8px 0 20px}
.de-hero h1{font-size:clamp(1.8rem,4vw,3rem);line-height:1.12;color:#174d31;margin-bottom:12px}
.de-card{background:white;border:1px solid #e1e8e1;border-radius:14px;padding:16px;margin:8px 0;box-shadow:0 2px 8px rgba(20,60,30,.04)}
.small-muted{color:#58665c;font-size:.9rem}.demo{background:#fff5d9;border-radius:7px;padding:7px 10px;font-size:.82rem}
.stButton>button{min-height:42px;border-radius:9px;font-weight:600}
@media(max-width:640px){.block-container{padding:1rem .75rem}.de-hero{padding:20px 16px}}
</style>""", unsafe_allow_html=True)

def txt(key): return t(key, lang)
def go(page): st.session_state.page=page

def sidebar():
    with st.sidebar:
        st.markdown("## 🏡 Daily Ease")
        choice=st.selectbox(txt("language"), ["English","हिन्दी","Hinglish"], index={"en":0,"hi":1,"hinglish":2}[lang], key="language_picker")
        mapped={"English":"en","हिन्दी":"hi","Hinglish":"hinglish"}[choice]
        if mapped != st.session_state.language:
            st.session_state.language=mapped; st.rerun()
        st.divider()
        if st.button(txt("home"), use_container_width=True): go("home")
        if st.button(txt("explore"), use_container_width=True): go("explore")
        if st.button(txt("how"), use_container_width=True): go("how")
        if st.button(txt("worker"), use_container_width=True): go("worker")
        if st.button(txt("assistant"), use_container_width=True): go("assistant")
        if st.session_state.user:
            st.caption(f"{st.session_state.user['name']} · {st.session_state.user['role']}")
            if st.button(txt("profile"), use_container_width=True): go("profile")
            if st.button(txt("requests"), use_container_width=True): go("requests")
            if st.session_state.user["role"]=="admin" and st.button(txt("admin"), use_container_width=True): go("admin")
            if st.button(txt("logout"), use_container_width=True): st.session_state.user=None; go("home"); st.rerun()
        else:
            if st.button(txt("login"), use_container_width=True): go("login")
            if st.button(txt("register"), use_container_width=True): go("register")
        st.divider(); st.caption(txt("footer"))

sidebar()
user=st.session_state.user

if st.session_state.page=="home":
    st.markdown(f'<div class="de-hero"><h1>{txt("hero")}</h1><p>{txt("hero_text")}</p></div>', unsafe_allow_html=True)
    a,b=st.columns([1,1])
    with a:
        if st.button(txt("find"), type="primary", use_container_width=True): go("explore"); st.rerun()
    with b:
        if st.button(txt("register_worker"), use_container_width=True): go("worker"); st.rerun()
    st.subheader(txt("explore"))
    categories=["Electrician","Plumber","Home Cleaning","Cook","Tutor","Carpenter","Painter","Beautician","Gardener","Delivery Helper","Appliance Repair","Other"]
    cols=st.columns(3)
    for i,cat in enumerate(categories):
        with cols[i%3]:
            if st.button(f"{cat}", key=f"cat_{cat}", use_container_width=True): st.session_state.search_category=cat; go("explore"); st.rerun()
    st.subheader(txt("how")); cols=st.columns(3)
    for col,key in zip(cols,["how_1","how_2","how_3"]):
        with col: st.markdown(f'<div class="de-card"><b>{txt(key)}</b></div>',unsafe_allow_html=True)
    st.info(txt("not_payment"))
elif st.session_state.page=="explore":
    st.title(txt("explore"))
    c1,c2,c3=st.columns([2,1,1])
    with c1: query=st.text_input(txt("search"))
    categories=["All categories","Electrician","Plumber","Home Cleaning","Cook","Tutor","Carpenter","Painter","Beautician","Gardener","Delivery Helper","Appliance Repair","Other"]
    with c2: category=st.selectbox(txt("category"),categories,index=categories.index(st.session_state.get("search_category","All categories")) if st.session_state.get("search_category","All categories") in categories else 0)
    with c3: locality=st.text_input(txt("locality"))
    if st.button(txt("clear")): st.session_state.search_category="All categories"; st.rerun()
    workers=search_workers(query,category,locality)
    st.caption(f"{len(workers)}")
    if not workers: st.info(txt("no_results"))
    for w in workers:
        with st.container(border=True):
            col1,col2=st.columns([1,4])
            with col1:
                if w["photo_path"] and Path(w["photo_path"]).exists(): st.image(w["photo_path"],width=110)
                else: st.markdown("### 👤")
            with col2:
                st.subheader(w["name"]); st.write(f"**{w['category']}** · {w['locality']}")
                st.write(w["skills"] or "—"); st.caption(f"{w['experience_years']} years · {w['price']} · {w['availability']}")
                st.caption(f"{txt('verification')}: {w['verification_status']}")
                if w["is_demo"]: st.markdown(f'<div class="demo">{txt("demo")}</div>',unsafe_allow_html=True)
                if user and user["role"]=="customer" and not w["is_demo"]:
                    with st.expander(txt("send_request")):
                        with st.form(f"req_{w['user_id']}"):
                            desc=st.text_area(txt("description")); loc=st.text_input(txt("location"),value=user.get("locality","")); when=st.text_input(txt("preferred"),value="Flexible")
                            submitted=st.form_submit_button(txt("send_request"))
                            if submitted:
                                try: create_request(user["id"],w["user_id"],desc,loc,when); st.success(txt("request_sent"))
                                except Exception as e: st.error(str(e))
                elif w["is_demo"]: st.caption("Demo profiles cannot receive bookings.")
                elif not user: st.caption(txt("need_login"))
elif st.session_state.page in ("login","register","worker"):
    worker_mode=st.session_state.page=="worker"
    is_register=st.session_state.page in ("register","worker")
    st.title(txt("register") if is_register else txt("login"))
    if is_register:
        role_default="worker" if worker_mode else "customer"
        with st.form("register_form"):
            name=st.text_input(txt("name")); email=st.text_input(txt("email")); password=st.text_input(txt("password"),type="password",help=txt("password_hint")); locality=st.text_input(txt("locality"))
            role=st.selectbox(txt("role"),["customer","worker"],index=1 if role_default=="worker" else 0,format_func=lambda x:txt(x if x=="customer" else "worker_role"))
            ok=st.form_submit_button(txt("submit"),type="primary")
            if ok:
                try: register_user(name,email,password,locality,role); st.success("Account created. Please log in."); go("login")
                except Exception as e: st.error(str(e))
    else:
        with st.form("login_form"):
            email=st.text_input(txt("email")); password=st.text_input(txt("password"),type="password"); ok=st.form_submit_button(txt("sign_in"),type="primary")
            if ok:
                found=authenticate(email,password)
                if found: st.session_state.user=found; go("home"); st.rerun()
                else: st.error(txt("login_failed"))
elif st.session_state.page=="profile":
    if not user: st.warning(txt("need_login"))
    elif user["role"]!="worker": st.info("Worker profiles are available to worker accounts.")
    else:
        with get_session() as s:
            u=s.get(User,user["id"]); p=u.worker_profile
            current={"category":p.category,"skills":p.skills,"bio":p.bio,"experience_years":p.experience_years,"price":p.price,"availability":p.availability,"languages":p.languages}
        st.title(txt("profile_title"))
        with st.form("profile_form"):
            category=st.selectbox(txt("category"),["Electrician","Plumber","Home Cleaning","Cook","Tutor","Carpenter","Painter","Beautician","Gardener","Delivery Helper","Appliance Repair","Other"],index=["Electrician","Plumber","Home Cleaning","Cook","Tutor","Carpenter","Painter","Beautician","Gardener","Delivery Helper","Appliance Repair","Other"].index(current["category"]) if current["category"] in ["Electrician","Plumber","Home Cleaning","Cook","Tutor","Carpenter","Painter","Beautician","Gardener","Delivery Helper","Appliance Repair","Other"] else 11)
            skills=st.text_input(txt("skills"),value=current["skills"]); bio=st.text_area(txt("bio"),value=current["bio"]); exp=st.number_input(txt("experience_label"),0,80,current["experience_years"]); price=st.text_input(txt("price"),value=current["price"]); availability=st.text_input(txt("availability"),value=current["availability"]); languages=st.text_input(txt("languages"),value=current["languages"])
            ok=st.form_submit_button(txt("save"),type="primary")
            if ok:
                try: update_worker_profile(user["id"],category,skills,bio,exp,price,availability,languages); st.success(txt("profile_saved")); st.rerun()
                except Exception as e: st.error(str(e))
        st.markdown(f"**{txt('upload')}**")
        photo=st.file_uploader(txt("photo"),type=["jpg","jpeg","png"])
        if photo:
            if photo.size>MAX_IMAGE_BYTES: st.error("File is larger than 5 MB.")
            else:
                try:
                    im=Image.open(photo); im.verify(); ext=".png" if photo.type=="image/png" else ".jpg"; dest=UPLOAD_DIR/f"worker_{user['id']}{ext}"
                    photo.seek(0); im=Image.open(photo).convert("RGB"); im.save(dest,format="JPEG",quality=88); update_worker_photo(user["id"],str(dest)); st.success("Photo saved."); st.rerun()
                except (UnidentifiedImageError, OSError): st.error("This image could not be read. Upload a valid JPG or PNG.")
elif st.session_state.page=="requests":
    if not user: st.warning(txt("need_login"))
    else:
        st.title(txt("requests")); rows=list_requests(user["id"],user["role"])
        if not rows: st.info(txt("no_requests"))
        for r in rows:
            with st.container(border=True):
                st.write(f"**#{r['id']} · {r['status']}**")
                st.write(r["description"]); st.caption(f"{r['customer_name']} → {r['worker_name']} · {r['location']} · {r['preferred_time']}")
                choices=[]
                if user["role"]=="worker": choices={"Pending":[("Accepted",txt("accept")),("Rejected",txt("reject"))],"Accepted":[("In Progress",txt("in_progress"))],"In Progress":[("Completed",txt("complete"))]}.get(r["status"],[])
                if user["role"]=="customer" and r["status"]=="Pending": choices=[("Cancelled",txt("cancel"))]
                for new_status,label in choices:
                    if st.button(label,key=f"status_{r['id']}_{new_status}"):
                        try: change_request_status(r["id"],user["id"],user["role"],new_status); st.success("Status updated."); st.rerun()
                        except Exception as e: st.error(str(e))
elif st.session_state.page=="admin":
    if not user or user["role"]!="admin": st.error("Admin access required.")
    else:
        st.title(txt("admin")); stats=admin_stats(); cols=st.columns(4)
        for col,(k,v) in zip(cols,stats.items()): col.metric(k.title(),v)
        st.subheader("Worker profiles")
        with get_session() as s:
            profiles=s.execute(select(WorkerProfile,User).join(User)).all()
            for p,u in profiles:
                with st.container(border=True):
                    st.write(f"**{u.name}** · {p.category} · {u.locality} · {p.verification_status}")
                    if p.is_demo: st.caption("Demo profile")
                    if st.button("Toggle active",key=f"toggle_{p.id}"):
                        p.is_active=not p.is_active; s.commit(); st.rerun()
        st.caption(txt("admin_note"))
elif st.session_state.page=="assistant":
    st.title(txt("assistant")); suggestions=["faq_search","faq_register","faq_request","faq_status","faq_language","faq_photo"]
    for key in suggestions:
        if st.button(txt(key),key=f"faq_{key}"): st.session_state.last_answer=answer(txt(key),lang)
    q=st.text_input(txt("ask"))
    if st.button(txt("submit"),key="ask_assistant") and q: st.session_state.last_answer=answer(q,lang)
    if st.session_state.get("last_answer"): st.info(st.session_state.last_answer)
elif st.session_state.page=="how":
    st.title(txt("how"))
    for i,k in enumerate(["how_1","how_2","how_3"],1): st.markdown(f"### {i}. {txt(k)}")
    st.info(txt("not_payment")); st.subheader(txt("support")); st.write("For this demo, contact the project maintainer through the repository owner. No staffed support channel is configured.")

st.divider()
left,right=st.columns(2)
with left: st.caption("© Daily Ease · Local Help. Trusted People. Easier Everyday Living.")
with right: st.caption(txt("not_payment"))
