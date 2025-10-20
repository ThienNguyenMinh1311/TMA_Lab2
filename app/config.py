import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
KB_DIR = os.path.join(BASE_DIR, "kb_storage")
LOG_FILE = os.path.join(BASE_DIR, "logs", "system.log")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 ngày

# Tạo folder nếu chưa có
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(KB_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
