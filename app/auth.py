from fastapi import APIRouter, HTTPException, Cookie, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import timedelta, datetime
from jose import jwt
from fastapi.templating import Jinja2Templates

import app

from .users_db import fake_users_db, verify_password
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from .utils import write_log

auth_router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(access_token: str = Cookie(None)):
    from .users_db import fake_users_db
    from jose import jwt
    from fastapi import HTTPException

    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = fake_users_db.get(username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return {"username": username, "role": role}
    except Exception:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

@auth_router.get("/", response_class=HTMLResponse)
async def login_page(request: Request): 
    return templates.TemplateResponse("login.html", {"request": request})

@auth_router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        write_log(f"Failed login attempt: {username}")
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": user["username"], "role": user["role"]}, expires_delta=access_token_expires)
    response = JSONResponse({"message": "Login successful", "username": user["username"], "role": user["role"]})
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60, path="/")
    write_log(f"Login success: {user['username']} ({user['role']})")
    return response
