from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from .auth import auth_router
from .dashboard import dashboard_router
from .lawyer_dashboard import router as lawyer_router
from .admin_dashboard import router as admin_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Law Office Document Management Backend")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/dataset", StaticFiles(directory="app/dataset"), name="dataset")

templates = Jinja2Templates(directory="app/templates")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(lawyer_router)
app.include_router(admin_router)
