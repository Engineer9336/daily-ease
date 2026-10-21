from datetime import datetime, timezone
from sqlalchemy import create_engine, String, Integer, Boolean, DateTime, ForeignKey, Text, Float, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from .config import DATABASE_URL

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="customer", index=True)
    locality: Mapped[str] = mapped_column(String(160), default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    worker_profile: Mapped["WorkerProfile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")

class WorkerProfile(Base):
    __tablename__ = "worker_profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(80), index=True)
    skills: Mapped[str] = mapped_column(Text, default="")
    bio: Mapped[str] = mapped_column(Text, default="")
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    price: Mapped[str] = mapped_column(String(100), default="Discuss with worker")
    availability: Mapped[str] = mapped_column(String(100), default="Contact for availability")
    languages: Mapped[str] = mapped_column(String(200), default="Hindi")
    photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(30), default="Unverified")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    user: Mapped[User] = relationship(back_populates="worker_profile")

class ServiceRequest(Base):
    __tablename__ = "service_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    worker_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    service_location: Mapped[str] = mapped_column(String(200), nullable=False)
    preferred_time: Mapped[str] = mapped_column(String(100), default="Flexible")
    status: Mapped[str] = mapped_column(String(30), default="Pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

_engine = None
_Session = None

def configure_database(url: str | None = None):
    global _engine, _Session
    if _engine is not None:
        _engine.dispose()
    db_url = url or DATABASE_URL
    kwargs = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    _engine = create_engine(db_url, future=True, pool_pre_ping=True, connect_args=kwargs)
    _Session = sessionmaker(bind=_engine, expire_on_commit=False)
    Base.metadata.create_all(_engine)
    return _engine

def get_session():
    global _engine, _Session
    if _Session is None: configure_database()
    return _Session()

def init_db(url: str | None = None): return configure_database(url)

def seed_demo_data():
    from .auth import hash_password
    with get_session() as s:
        if s.scalar(select(User).where(User.email == "demo.electrician@dailyease.local")): return
        samples = [
            ("Ramesh Kumar", "demo.electrician@dailyease.local", "Electrician", "Wiring, fan repair, switches", "Gorakhpur", "₹300 onwards"),
            ("Sunita Devi", "demo.cleaner@dailyease.local", "Home Cleaning", "Home cleaning, kitchen cleaning", "Gorakhpur", "₹500 per visit"),
            ("Imran Ansari", "demo.plumber@dailyease.local", "Plumber", "Tap repair, pipe fitting, leakage", "Sahjanwa", "₹250 onwards"),
            ("Pooja Singh", "demo.tutor@dailyease.local", "Tutor", "Primary classes, Hindi, Maths", "Gorakhpur", "₹200 per hour"),
        ]
        for name, email, category, skills, locality, price in samples:
            u = User(name=name, email=email, password_hash=hash_password("DemoOnly-NotForProduction!"), role="worker", locality=locality)
            u.worker_profile = WorkerProfile(category=category, skills=skills, bio="Sample profile for demonstration only.", experience_years=2, price=price, availability="Contact for availability", languages="Hindi, English", verification_status="Unverified", is_demo=True)
            s.add(u)
        s.commit()
