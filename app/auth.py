from fastapi import APIRouter, HTTPException, Cookie, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import timedelta, datetime
from jose import jwt
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from passlib.context import CryptContext
from app.config import MONGODB_URI
from dotenv import load_dotenv
import os
import certifi

# Load environment variables
load_dotenv()

def connect_to_mongodb():
    try:
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            tls=True,
            tlsCAFile=certifi.where()
        )
        client.admin.command('ping')  # Test connection
        db = client['mydatabase']
        return db
    except ConnectionFailure as e:
        raise Exception(f"Failed to connect to MongoDB: {e}")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")

# Initialize MongoDB
db = connect_to_mongodb()

# Password verification setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Configuration
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Utility function for logging
def write_log(message: str):
    print(f"LOG: {message}")  # Replace with actual logging logic if needed

auth_router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

class LoginRequest(BaseModel):
    username: str
    password: str

def authenticate_user(username: str, password: str):
    users_collection = db['users']
    user = users_collection.find_one({"username": username})
    if not user:
        return None
    if not verify_password(password, user.get("hashed_password", "")):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        users_collection = db['users']
        user = users_collection.find_one({"username": username})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return {"username": username, "role": user["role"], "access": user.get("access", [])}
    except Exception:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

@auth_router.get("/", response_class=HTMLResponse)
async def login_page(request: Request): 
    return templates.TemplateResponse("login.html", {"request": request})

@auth_router.post("/login")
async def login(request: LoginRequest):
    user = authenticate_user(request.username, request.password)
    if not user:
        write_log(f"Failed login attempt: {request.username}")
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": user["username"], "role": user["role"]}, expires_delta=access_token_expires)
    response = JSONResponse({"message": "Login successful", "username": user["username"], "role": user["role"]})
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60, path="/")
    write_log(f"Login success: {user['username']} ({user['role']})")
    return response