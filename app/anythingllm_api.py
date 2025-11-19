from app.config import ANYTHING_API_BASE, ANYTHING_API_KEY, MONGODB_URI
import requests
from fastapi import UploadFile, File, HTTPException
import requests
from pymongo import MongoClient
import requests
import os
import re

def create_new_workspace(username: str):
    url = f"{ANYTHING_API_BASE}/workspace/new"
    workspace_name = f"{username}_workspace"
    HEADERS_JSON = {
        "Authorization": f"Bearer {ANYTHING_API_KEY}",
        "accept": "application/json",
    }
    payload = {
        "name": workspace_name,
        "chatProvider": "openrouter",
        "chatModel": "qwen/qwen3-30b-a3b:free"
    }
    res = requests.post(url, headers=HEADERS_JSON, json=payload)
    if res.status_code == 200:
        return res.text
    else:
        raise Exception(f"Failed to create workspace: {res.status_code} - {res.text}")

def get_chatbot_history(username: str, thread_slug: str = None):
    """
    Lấy lịch sử chat từ AnythingLLM API dựa trên thread slug hiện tại
    """

    user_chats = []
    llm_replies = []
    
    if thread_slug == None:
        # Nếu không có thread_slug thì lấy lịch sử chat chung của workspace
        url = f"{ANYTHING_API_BASE}/workspace/{username}_workspace/chats"
        HEADERS_JSON = {
            "Authorization": f"Bearer {ANYTHING_API_KEY}",
            "accept": "application/json",
        }
        res = requests.get(url, headers=HEADERS_JSON)
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=f"Lỗi khi lấy lịch sử chat: {res.text}")

        response_json = res.json()
        
        for msg in response_json["history"]:
            if msg["role"] == "user":
                user_chats.append(msg["content"])
            elif msg["role"] == "assistant":
                # Loại bỏ phần <think>...</think>
                cleaned_content = re.sub(r"<think>.*?</think>", "", msg["content"], flags=re.DOTALL).strip()
                llm_replies.append(cleaned_content)
                
        return user_chats, llm_replies
    
    else:
        # Nếu có thread_slug thì lấy lịch sử chat của thread đó
        url = f"{ANYTHING_API_BASE}/workspace/{username}_workspace/thread/{thread_slug}/chats"
        HEADERS_JSON = {
            "Authorization": f"Bearer {ANYTHING_API_KEY}",
            "accept": "application/json",
        }
        res = requests.get(url, headers=HEADERS_JSON)
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=f"Lỗi khi lấy lịch sử chat: {res.text}")

        response_json = res.json()
        
        for msg in response_json["history"]:
            if msg["role"] == "user":
                user_chats.append(msg["content"])
            elif msg["role"] == "assistant":
                # Loại bỏ phần <think>...</think>
                cleaned_content = re.sub(r"<think>.*?</think>", "", msg["content"], flags=re.DOTALL).strip()
                llm_replies.append(cleaned_content)
                
        return user_chats, llm_replies

def chat(username: str, thread_slug: str = None, message: str = None, mode: str = "chat"):
    if thread_slug is None:
        user_chats, llm_replies = get_chatbot_history(username)
        url = f"{ANYTHING_API_BASE}/workspace/{username}_workspace/chat"
        HEADERS_JSON = {
            "Authorization": f"Bearer {ANYTHING_API_KEY}",
            "accept": "application/json",   
        }
        if mode != "chat" and mode != "query":
            raise HTTPException(status_code=400, detail="Invalid mode. Must be 'chat' or 'query'.")
        else:
            payload = {
                "message": message,
                "mode": mode,
                "reset": False
            }
        res = requests.post(url, headers=HEADERS_JSON, json=payload)
    else:
        url = f"{ANYTHING_API_BASE}/workspace/{username}_workspace/thread/{thread_slug}/chats"
        HEADERS_JSON = {
            "Authorization": f"Bearer {ANYTHING_API_KEY}",
            "accept": "application/json",   
        }
        if mode != "chat" and mode != "query":
            raise HTTPException(status_code=400, detail="Invalid mode. Must be 'chat' or 'query'.")
        else:
            payload = {
                "message": message,
                "mode": mode,
                "reset": False
            }
        res = requests.post(url, headers=HEADERS_JSON, json=payload)
        
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=f"Lỗi khi gửi tin nhắn đến chatbot: {res.text}")
    else:
        response_json = res.json()
        raw_response = response_json["textResponse"]
        cleaned_response = re.sub(r"<think>.*?</think>", "", raw_response, flags=re.DOTALL).strip()
        return cleaned_response

def new_thread(username: str, thread_name: str, thread_slug: str):
    # ==============================
    # 1️⃣ Gọi API AnythingLLM để tạo thread mới
    # ==============================
    url = f"{ANYTHING_API_BASE}/workspace/{username}_workspace/thread/new"
    HEADERS_JSON = {
        "Authorization": f"Bearer {ANYTHING_API_KEY}",  
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "name": thread_name,
        "slug": thread_slug
    }

    res = requests.post(url, headers=HEADERS_JSON, json=payload)
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=f"Lỗi khi tạo thread mới: {res.text}")

    data = res.json()
    print(f"✅ New thread created: {data}")

    # ==============================
    # 2️⃣ Kết nối MongoDB
    # ==============================
    try:
        client = MongoClient(MONGODB_URI)
        db = client["mydatabase"] 
        users_collection = db["users"]

        # ==============================
        # 3️⃣ Cập nhật field 'slugs'
        # ==============================
        user_doc = users_collection.find_one({"username": username})

        if not user_doc:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy user '{username}' trong MongoDB.")

        # Nếu user chưa có field 'slugs', tạo mới
        slugs = user_doc.get("slugs", [])

        if thread_slug not in slugs:
            slugs.append(thread_slug)
            users_collection.update_one(
                {"username": username},
                {"$set": {"slugs": slugs}}
            )
            print(f"✅ Đã thêm slug '{thread_slug}' vào user '{username}' trong MongoDB.")
        else:
            print(f"⚠️ Slug '{thread_slug}' đã tồn tại trong user '{username}' — bỏ qua cập nhật.")

        client.close()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật MongoDB: {e}")

    return data

def exist_user_workspaces(username: str):
    url = f"{ANYTHING_API_BASE}/workspaces"
    HEADERS_JSON = {
        "Authorization": f"Bearer {ANYTHING_API_KEY}",  
        "accept": "application/json",
    }
    
    res = requests.get(url, headers=HEADERS_JSON)
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=f"Lỗi khi lấy danh sách workspaces: {res.text}")
    
    if f"{username}_workspace" in res.text:
        return True
    return False

def drop_user_workspace(username: str):
    url = f"{ANYTHING_API_BASE}/workspace/{username}_workspace"
    HEADERS_JSON = {
        "Authorization": f"Bearer {ANYTHING_API_KEY}",  
        "accept": "*/*",
    }
    
    res = requests.delete(url, headers=HEADERS_JSON)
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=f"Lỗi khi xóa workspace: {res.text}")

def get_document_name(folder_name: str, document_name: str) -> list:
    url = f"{ANYTHING_API_BASE}/documents/folder/{folder_name}"
    HEADERS_UPLOAD = {
            "Authorization": f"Bearer {ANYTHING_API_KEY}",
            "accept": "application/json",
        }
    response = requests.get(url, headers=HEADERS_UPLOAD)
    if response.status_code != 200:
        raise Exception(f"Error fetching documents: {response.text}")
    data = response.json()
    for doc in data.get("documents", []):
        if document_name in doc.get("name", ""):
            return doc["name"]
        
    return "Not found"

def check_exist_document_in_workspace(username: str, document_title: str):
    url = f"{ANYTHING_API_BASE}/documents/folder/custom-documents"

    HEADERS_JSON = {
        "Authorization": f"Bearer {ANYTHING_API_KEY}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }

    response = requests.get(url, headers=HEADERS_JSON)

    if response.status_code == 200:
        data = response.json()
        for item in data['documents']:
            if item['title'] == document_title:
                return True
        return False
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to get documents: {response.text}")

def upload_document_to_workspace(username: str, file: UploadFile = File(...)):
    """
    Kiểm tra tài liệu đã tồn tại trong custom-documents chưa
    Nếu chưa thì thêm vào custom-documents và workspace của người dùng
    Upload tài liệu vào workspace của người dùng trong AnythingLLM
    (Chuẩn hóa theo API /document/upload/custom-documents)
    """
    if not check_exist_document_in_workspace(username, file.filename):
        workspace_name = f"{username}_workspace"
        upload_url = f"{ANYTHING_API_BASE}/document/upload/custom-documents"

        HEADERS_UPLOAD = {
            "Authorization": f"Bearer {ANYTHING_API_KEY}",
            "accept": "application/json",
        }

        try:
            # Gửi file trực tiếp từ request người dùng
            files = {"file": (file.filename, file.file, file.content_type or "application/octet-stream")}

            res = requests.post(upload_url, headers=HEADERS_UPLOAD, files=files)

            if res.status_code != 200:
                raise HTTPException(status_code=res.status_code, detail=f"Lỗi khi upload tài liệu: {res.text}")

            data = res.json()
            print(f"✅ Document uploaded and embedded")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi khi gọi AnythingLLM API: {e}")
    
    if get_document_name("custom-documents", file.filename) == "Not found":
        raise HTTPException(status_code=404, detail="Tài liệu không tồn tại trong custom-documents sau khi upload.")    
    else:
        filename = get_document_name("custom-documents", file.filename)
        url = f"{ANYTHING_API_BASE}/workspace/{username}_workspace/update-embeddings"
        payload = {
            "adds": [f"custom-documents/{filename}"]
        }
        HEADERS_UPLOAD = {
                "Authorization": f"Bearer {ANYTHING_API_KEY}",
                "accept": "application/json",
            }
        res = requests.post(url, headers=HEADERS_UPLOAD, json=payload)
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=f"Lỗi khi thêm tài liệu vào workspace: {res.text}")
        print(f"Debug {filename}")
    