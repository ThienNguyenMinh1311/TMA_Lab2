from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import List, Optional
import os
from .users_db import get_hashed as get_hashed_password
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

DATASET_DIR = Path("./dataset")
DATASET_DIR.mkdir(exist_ok=True, parents=True)

# MongoDB connection setup
MONGODB_URI = "mongodb+srv://tian_ng:matkhau@tiandata.uovixjo.mongodb.net/"

def connect_to_mongodb():
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')  # Test connection
        db = client['mydatabase']
        return db
    except ConnectionFailure as e:
        raise Exception(f"Failed to connect to MongoDB: {e}")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")

db = connect_to_mongodb()

# =========================
# 👤 QUẢN LÝ NHÂN VIÊN
# =========================
@router.get("/users")
def get_users():
    users_collection = db['users']
    users = [
        {
            "username": user["username"],
            "role": user["role"],
            "access": user.get("access", [])
        }
        for user in users_collection.find()
    ]
    return JSONResponse({"users": users})

@router.post("/users")
def add_user(user: dict):
    username = user.get("username")
    role = user.get("role")
    password = user.get("password")
    access = user.get("access", [])

    if not username or not role or not password:
        raise HTTPException(status_code=400, detail="Missing username, role, or password")

    users_collection = db['users']
    try:
        users_collection.insert_one({
            "username": username,
            "hashed_password": get_hashed_password(password),
            "role": role,
            "access": access
        })
        return JSONResponse({"message": f"User '{username}' added successfully."})
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="User already exists")

@router.put("/users/{username}")
async def update_user(username: str, request: Request):
    """
    Cập nhật role, password và access cùng lúc.
    Body JSON:
    {
        "role": "lawyer/admin",
        "password": "newpassword" (optional),
        "documents": ["doc1.txt", "doc2.pdf"] (optional)
    }
    """
    data = await request.json()
    role = data.get("role")
    password = data.get("password")
    documents = data.get("documents")

    if not role:
        raise HTTPException(status_code=400, detail="Role is required")

    users_collection = db['users']
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = {"role": role}
    if password:
        update_data["hashed_password"] = get_hashed_password(password)
    if documents is not None:
        # Lọc các tên tài liệu tồn tại trong DATASET_DIR
        valid_docs = [doc for doc in documents if (DATASET_DIR / doc).exists()]
        update_data["access"] = valid_docs

    users_collection.update_one({"username": username}, {"$set": update_data})
    return JSONResponse({"message": f"User '{username}' updated successfully."})

@router.delete("/users/{username}")
def delete_user(username: str):
    users_collection = db['users']
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user["role"] == "admin":
        raise HTTPException(status_code=403, detail="Admin cannot be deleted")

    result = users_collection.delete_one({"username": username})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse({"message": f"User '{username}' deleted successfully."})

# =========================
# 📂 QUẢN LÝ TÀI LIỆU
# =========================
@router.get("/documents")
def get_documents():
    files = [
        f.name for f in DATASET_DIR.iterdir()
        if f.is_file() and f.suffix in [".txt", ".pdf", ".docx"]
    ]
    return JSONResponse({"documents": files})

@router.post("/documents")
def add_document(file: dict):
    filename = file.get("filename")
    if not filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    path = DATASET_DIR / filename
    if path.exists():
        raise HTTPException(status_code=400, detail="Document already exists")

    path.write_text("Nội dung mới được tạo.")
    return JSONResponse({"message": f"Document '{filename}' added successfully."})

@router.delete("/documents/{filename}")
def delete_document(filename: str):
    path = DATASET_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    os.remove(path)

    users_collection = db['users']
    users_collection.update_many(
        {"access": filename},
        {"$pull": {"access": filename}}
    )
    return JSONResponse({"message": f"Document '{filename}' deleted successfully."})
