from passlib.context import CryptContext

# Tạo context cho bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Database mẫu (giả lập)
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": get_hashed("adminpass"),
        "role": "admin",
        "access": []
    },
    "lawyer1": {
        "username": "lawyer1",
        "hashed_password": get_hashed("lawyerpass"),
        "role": "lawyer",
        "access": ["case_1", "case_2", "case_3"]
    },
    "lawyer2": {
        "username": "lawyer2",
        "hashed_password": get_hashed("lawyerpass"),
        "role": "lawyer",
        "access": ["case_4", "case_5", "case_6"]
    }
}