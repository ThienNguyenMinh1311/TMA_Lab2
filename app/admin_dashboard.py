from fastapi import APIRouter, HTTPException, Request, UploadFile, Form, Depends
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse 
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import UploadFile, File
import shutil
import os
import requests
from pathlib import Path
from typing import List, Optional
import os
from .users_db import get_hashed as get_hashed_password
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from app.config import MONGODB_URI, ANYTHING_API_KEY, ANYTHING_API_BASE
from app.anythingllm_api import (
    exist_user_workspaces, 
    drop_user_workspace, 
    create_new_workspace, 
    upload_document_to_workspace, 
    check_exist_document_in_workspace
)
from app.auth import get_current_user
import certifi

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

# =========================
# ⚙️ MongoDB Setup
# =========================

def connect_to_mongodb():
    try:
        client = MongoClient(
            MONGODB_URI, 
            serverSelectionTimeoutMS=5000,
            tlsCAFile=certifi.where())
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
# 📁 Templates & dataset
# =========================
templates = Jinja2Templates(directory="./app/templates")
DATASET_DIR = Path("./app/dataset")
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
    """Xóa người dùng (trừ admin) + xóa luôn workspace"""
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("role") == "admin":
        raise HTTPException(status_code=403, detail="Cannot delete admin user")

    # 🔹 Xóa workspace trước (nếu có)
    if exist_user_workspaces(username):
        try:
            drop_user_workspace(username)
        except Exception as e:
            print(f"⚠️ Không thể xóa workspace của {username}: {e}")

    users_collection.delete_one({"username": username})
    return JSONResponse({"message": f"User '{username}' và workspace liên quan đã được xóa."})

# =========================
# 🔹 QUẢN LÝ TÀI LIỆU LOCAL
# =========================

@router.get("/documents")
async def list_documents():
    files = [f.name for f in DATASET_DIR.iterdir() if f.is_file()]
    return JSONResponse({"documents": files})


@router.post("/documents/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    uploaded_files = []
    for file in files:
        dest_path = DATASET_DIR / file.filename
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded_files.append(file.filename)
    return JSONResponse({"message": "Upload thành công", "uploaded": uploaded_files})


@router.delete("/documents/{filename}")
async def delete_document(filename: str):
    file_path = DATASET_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    os.remove(file_path)
    return JSONResponse({"message": f"File '{filename}' deleted successfully."})

# ==============================
# 🔹 AnythingLLM Configuration
# ==============================
HEADERS_JSON = {
    "Authorization": f"Bearer {ANYTHING_API_KEY}",
    "Content-Type": "application/json",
    "accept": "application/json",
}

HEADERS_UPLOAD = {
    "Authorization": f"Bearer {ANYTHING_API_KEY}",
    "accept": "application/json",
}

@router.post("/create-workspace/{username}")
def create_workspace(username: str):
    """
    1. Kiểm tra workspace tồn tại
    2. Tạo workspace mới
    3. Tự động upload + embed tất cả file trong access của user
       (dùng upload_document_to_workspace đã bao gồm logic check + embed)
    """
    # --- Lấy thông tin user ---
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy người dùng {username}")

    workspace_name = f"{username}_workspace"

    # --- Kiểm tra workspace ---
    if exist_user_workspaces(username):
        raise HTTPException(status_code=400, detail=f"Workspace '{workspace_name}' đã tồn tại")

    # --- Tạo workspace ---
    create_new_workspace(username)

    # --- Upload và embed toàn bộ file access ---
    access_files = user.get("access", [])
    failed_files = []

    for filename in access_files:
        file_path = DATASET_DIR / filename

        if not file_path.exists():
            print(f"⚠️ File không tồn tại: {file_path}")
            failed_files.append(filename)
            continue

        try:
            # Mở file theo đúng dạng UploadFile của FastAPI
            with open(file_path, "rb") as f:
                upload_file = UploadFile(
                    filename=filename,
                    file=f
                )

                upload_document_to_workspace(username, upload_file)
                print(f"📄 Done: {filename}")

        except Exception as e:
            print(f"❌ Lỗi xử lý file {filename}: {e}")
            failed_files.append(filename)

    return {
        "message": f"Workspace '{workspace_name}' đã được tạo thành công!",
        "workspace": {"slug": workspace_name},
        "failed_files": failed_files
    }

# ----------------- 💬 CHATBOT -----------------
@router.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Hiển thị giao diện chatbot, có thể tạo thread mới hoặc upload tài liệu
    """
    username = current_user["username"]
    return templates.TemplateResponse("admin_chatbot.html", {"request": request, "username": username})
