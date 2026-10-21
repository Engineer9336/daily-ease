import hashlib, hmac, secrets
from sqlalchemy import select
from .db import get_session, User, ActivityLog

# PBKDF2 with per-password random salt; no plaintext password is stored.
def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"pbkdf2_sha256$310000${salt.hex()}${digest.hex()}"

def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, rounds, salt_hex, digest_hex = encoded.split("$")
        if scheme != "pbkdf2_sha256": return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(rounds)).hex()
        return hmac.compare_digest(actual, digest_hex)
    except (ValueError, TypeError): return False

def register_user(name: str, email: str, password: str, locality: str, role: str = "customer"):
    name, email, locality = name.strip(), email.strip().lower(), locality.strip()
    if len(name) < 2: raise ValueError("Please enter a name with at least 2 characters.")
    if "@" not in email or "." not in email.split("@")[-1]: raise ValueError("Please enter a valid email address.")
    if len(password) < 8: raise ValueError("Password must contain at least 8 characters.")
    if not locality: raise ValueError("Please enter your locality.")
    if role not in {"customer", "worker"}: raise ValueError("Invalid account role.")
    with get_session() as s:
        if s.scalar(select(User).where(User.email == email)): raise ValueError("An account with this email already exists.")
        user = User(name=name, email=email, password_hash=hash_password(password), locality=locality, role=role)
        s.add(user); s.flush()
        if role == "worker":
            from .db import WorkerProfile
            user.worker_profile = WorkerProfile(category="Other", is_demo=False)
        s.add(ActivityLog(actor_id=user.id, action="user_registered", details=f"role={role}"))
        s.commit(); s.refresh(user)
        return user.id

def authenticate(email: str, password: str):
    with get_session() as s:
        user = s.scalar(select(User).where(User.email == email.strip().lower(), User.active.is_(True)))
        if user and verify_password(password, user.password_hash): return {"id": user.id, "name": user.name, "email": user.email, "role": user.role, "locality": user.locality}
    return None
