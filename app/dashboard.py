from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .auth import get_current_user

templates = Jinja2Templates(directory="app/templates")
dashboard_router = APIRouter()

@dashboard_router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied: Admin only.")
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "username": current_user["username"], "role": current_user["role"]}
    )

# Route cho lawyer
@dashboard_router.get("/lawyer/dashboard", response_class=HTMLResponse)
async def lawyer_dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "lawyer":
        raise HTTPException(status_code=403, detail="Access denied: Lawyer only.")
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "username": current_user["username"], "role": current_user["role"]}
    )