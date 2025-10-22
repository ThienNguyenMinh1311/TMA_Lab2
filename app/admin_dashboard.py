from fastapi import APIRouter, HTTPException, Request, UploadFile, Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse 
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
from pathlib import Path
from typing import List, Optional
import os
from .users_db import get_hashed as get_hashed_password
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

# =========================
# ⚙️ MongoDB Setup
# =========================
MONGODB_URI = "mongodb+srv://tian_ng:matkhau@tiandata.uovixjo.mongodb.net/"

def connect_to_mongodb():
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        db = client["mydatabase"]
        return db
    except ConnectionFailure as e:
        raise Exception(f"Failed to connect to MongoDB: {e}")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")

db = connect_to_mongodb()
users_collection = db["users"]

# =========================
# 📂 Dataset directory
# =========================
DATASET_DIR = Path("./dataset")
DATASET_DIR.mkdir(exist_ok=True, parents=True)

# =========================
# 👤 QUẢN LÝ NHÂN VIÊN
# =========================

@router.get("/users")
def get_users():
    """Lấy danh sách toàn bộ người dùng"""
    users = [
        {
            "username": user["username"],
            "role": user.get("role", "lawyer"),
            "access": user.get("access", []),
        }
        for user in users_collection.find()
    ]
    return JSONResponse({"users": users})


@router.post("/users")
async def add_user(request: Request):
    """Thêm người dùng mới"""
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "lawyer")
    access = data.get("access", [])

    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing username or password")

    # Kiểm tra trùng username
    if users_collection.find_one({"username": username}):
        raise HTTPException(status_code=400, detail="User already exists")

    # Tạo người dùng mới
    new_user = {
        "username": username,
        "hashed_password": get_hashed_password(password),
        "role": role,
        "access": access,
    }

    users_collection.insert_one(new_user)
    return JSONResponse({"message": f"User '{username}' added successfully."})


@router.put("/users/{username}")
async def update_user(username: str, request: Request):
    """
    Cập nhật thông tin user (role, password, access/documents).
    Body JSON có thể gồm:
    {
        "role": "lawyer" hoặc "admin",
        "password": "newpass" (tùy chọn),
        "documents": ["case_1", "case_2"]
    }
    """
    data = await request.json()
    print("📩 DATA NHẬN ĐƯỢC:", data)

    role = data.get("role")
    password = data.get("password")
    documents = data.get("documents")  # ← Giao diện gửi lên là 'documents', không phải 'access'

    users_collection = db["users"]
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = {}

    # role
    if role and role != user.get("role"):
        update_data["role"] = role

    # password
    if password:
        update_data["hashed_password"] = get_hashed_password(password)

    # documents → access
    if documents is not None:
        # lọc chuỗi trắng, loại ký tự thừa
        access_clean = [x.strip().strip('"').strip("'") for x in documents if x.strip()]
        update_data["access"] = access_clean
        print("✅ ACCESS PARSED:", access_clean)

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    result = users_collection.update_one({"username": username}, {"$set": update_data})
    print("🧩 KẾT QUẢ UPDATE:", result.raw_result)

    if result.modified_count == 0:
        return JSONResponse({"message": f"No changes made for '{username}'."})

    return JSONResponse({"message": f"User '{username}' updated successfully."})



@router.delete("/users/{username}")
def delete_user(username: str):
    """Xóa người dùng (trừ admin)"""
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("role") == "admin":
        raise HTTPException(status_code=403, detail="Cannot delete admin user")

    users_collection.delete_one({"username": username})
    return JSONResponse({"message": f"User '{username}' deleted successfully."})


# =========================
# 📁 Templates & dataset
# =========================
templates = Jinja2Templates(directory="./app/templates")

DATASET_DIR = Path("./app/dataset")
DATASET_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# 🔹 QUẢN LÝ TÀI LIỆU LOCAL
# =========================

@router.get("/documents", response_class=HTMLResponse)
async def admin_documents(request: Request):
    """Hiển thị danh sách tài liệu local"""
    files = [f.name for f in DATASET_DIR.iterdir() if f.is_file()]
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "files": files}
    )


@router.post("/upload")
async def upload_document(file: UploadFile):
    """Xử lý tải lên tài liệu"""
    dest_path = DATASET_DIR / file.filename
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return RedirectResponse(url="/admin/documents", status_code=303)
