from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .auth import get_current_user

templates = Jinja2Templates(directory="app/templates")
dashboard_router = APIRouter()

@dashboard_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    role = current_user["role"]
    if role == "lawyer":
        return templates.TemplateResponse("index.html", {"request": request, "username": current_user["username"]})
    elif role == "admin":
        return templates.TemplateResponse("admin.html", {"request": request, "username": current_user["username"]})
    else:
        raise HTTPException(status_code=403, detail="Role not allowed")
