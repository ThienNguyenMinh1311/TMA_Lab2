from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from .auth import auth_router
from .dashboard import dashboard_router

app = FastAPI(title="Law Office Document Management Backend")

app.mount("/app/static", StaticFiles(directory="app/static"), name="app/static")
templates = Jinja2Templates(directory="app/static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(dashboard_router)
