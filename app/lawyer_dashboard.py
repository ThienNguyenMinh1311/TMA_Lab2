from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from .config import SECRET_KEY, ALGORITHM

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

# Initialize MongoDB
db = connect_to_mongodb()

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/lawyer", tags=["Lawyer Dashboard"])

DATASET_DIR = Path("./app/dataset/")

# ----------------- AUTH HELPER -----------------
def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        users_collection = db['users']
        user = users_collection.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

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
    allowed_docs = current_user.get("access", [])
    available_docs = []

    for doc_name in allowed_docs:
        file_path = DATASET_DIR / doc_name
        if file_path.exists():
            available_docs.append(doc_name)

    return JSONResponse({"documents": available_docs})
