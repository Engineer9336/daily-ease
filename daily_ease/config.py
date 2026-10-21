import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = Path(os.getenv("DAILY_EASE_UPLOAD_DIR", BASE_DIR / "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///" + str(BASE_DIR / "daily_ease.db"))
MAX_IMAGE_BYTES = 5 * 1024 * 1024
