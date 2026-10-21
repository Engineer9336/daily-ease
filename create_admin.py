"""Create or promote the first admin account from an interactive terminal."""
import getpass
from daily_ease.db import init_db, get_session, User
from daily_ease.auth import hash_password
from sqlalchemy import select

init_db()
email=input("Admin email: ").strip().lower()
name=input("Admin name: ").strip()
password=getpass.getpass("Admin password (min 12 chars): ")
if len(password)<12: raise SystemExit("Password must be at least 12 characters.")
with get_session() as s:
    user=s.scalar(select(User).where(User.email==email))
    if user:
        user.role="admin"; user.password_hash=hash_password(password); user.active=True
    else:
        user=User(name=name,email=email,password_hash=hash_password(password),role="admin",locality="")
        s.add(user)
    s.commit()
print("Admin account created/updated. Keep these credentials private.")
