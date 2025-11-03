import re
from fastapi import APIRouter, Request, Depends, HTTPException, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.auth import get_current_user
from app.config import MONGODB_URI, SECRET_KEY, ALGORITHM, ANYTHING_API_BASE, ANYTHING_API_KEY
from app.anythingllm_api import (
    get_chatbot_history,
    chat,
    upload_document_to_workspace,
    new_thread
)
import requests

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

# Initialize MongoDB
db = connect_to_mongodb()

templates = Jinja2Templates(directory="./app/templates")

router = APIRouter(prefix="/lawyer", tags=["Lawyer Dashboard"])

DATASET_DIR = Path("./app/dataset/")

# ----------------- DASHBOARD -----------------
@router.get("/dashboard", response_class=HTMLResponse)
async def lawyer_dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return templates.TemplateResponse("lawyer_dashboard.html", {"request": request, "username": username})

# ----------------- TÀI LIỆU -----------------
@router.get("/documents", response_class=JSONResponse)
async def get_lawyer_documents(current_user: dict = Depends(get_current_user)):
    """
    Trả danh sách tài liệu mà user có quyền truy cập (theo 'access' trong MongoDB)
    """
    print("✅ current_user:", current_user)

    allowed_docs = current_user.get("access", [])
    available_docs = []

    for doc_name in allowed_docs:
        file_path = DATASET_DIR / doc_name
        if file_path.exists():
            available_docs.append(doc_name)

    return JSONResponse({"documents": available_docs})

# ----------------- 💬 CHATBOT -----------------
@router.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Hiển thị giao diện chatbot, có thể tạo thread mới hoặc upload tài liệu
    """
    username = current_user["username"]
    return templates.TemplateResponse("chatbot.html", {"request": request, "username": username})


# ----------------- 📢 TẠO THREAD MỚI -----------------
@router.post("/chatbot/new-thread")
async def create_new_thread(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Gọi AnythingLLM API để tạo thread mới, đồng thời lưu slug vào MongoDB
    """
    data = await request.json()
    thread_name = data.get("thread_name")
    thread_slug = data.get("thread_slug")

    if not thread_name or not thread_slug:
        raise HTTPException(status_code=400, detail="Thiếu thread_name hoặc thread_slug")

    username = current_user["username"]

    try:
        response = new_thread(username=username, thread_name=thread_name, thread_slug=thread_slug)
        return JSONResponse({"message": "Tạo thread mới thành công", "data": response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo thread mới: {e}")


# ----------------- 📄 TẢI TÀI LIỆU -----------------
@router.post("/chatbot/upload-doc")
async def upload_doc_to_workspace(file: UploadFile, current_user: dict = Depends(get_current_user)):
    """
    Upload tài liệu vào workspace của người dùng trong AnythingLLM
    """
    username = current_user["username"]

    try:
        result = upload_document_to_workspace(username=username, file=file)
        return JSONResponse({"message": "Tải tài liệu thành công", "result": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tải tài liệu: {e}")


# ----------------- 💭 GỬI TIN NHẮN CHATBOT -----------------
@router.post("/chatbot/send-message")
async def send_chat_message(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Gửi tin nhắn tới chatbot của người dùng và trả về phản hồi
    """
    data = await request.json()
    message = data.get("message")
    thread_slug = data.get("thread_slug")  # Có thể là None
    mode = data.get("mode", "chat")

    if not message:
        raise HTTPException(status_code=400, detail="Tin nhắn trống")

    username = current_user["username"]

    try:
        reply = chat(username=username, thread_slug=thread_slug, message=message, mode=mode)
        return JSONResponse({"reply": reply})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi gửi tin nhắn: {e}")


# ----------------- 🕓 LỊCH SỬ TRÒ CHUYỆN -----------------
@router.get("/chatbot/history", response_class=JSONResponse)
async def get_chat_history(thread_slug: str = None, current_user: dict = Depends(get_current_user)):
    """
    Lấy lịch sử trò chuyện từ AnythingLLM để hiển thị giao diện chat
    """
    username = current_user["username"]

    try:
        user_chats, llm_replies = get_chatbot_history(username=username, thread_slug=thread_slug)
        return JSONResponse({"user_chats": user_chats, "llm_replies": llm_replies})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy lịch sử trò chuyện: {e}")


# # ----------------- 📁 DANH SÁCH THREADS CỦA USER -----------------
# @router.get("/chatbot/threads", response_class=JSONResponse)
# async def list_user_threads(current_user: dict = Depends(get_current_user)):
#     """
#     Trả về danh sách các thread (slug) mà user đã tạo — lưu trong MongoDB
#     """
#     username = current_user["username"]

#     try:
#         client = MongoClient(MONGODB_URI)
#         db = client["mydatabase"]
#         users_collection = db["users"]
#         user_doc = users_collection.find_one({"username": username}, {"_id": 0, "slugs": 1})
#         client.close()

#         if not user_doc:
#             raise HTTPException(status_code=404, detail="Không tìm thấy người dùng trong MongoDB.")

#         return JSONResponse({"threads": user_doc.get("slugs", [])})
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Lỗi khi truy xuất danh sách threads: {e}")

