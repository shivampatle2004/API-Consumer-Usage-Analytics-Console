"""
Unified Production App for Free Cloud Deployment (Render / Railway / Fly.io)
Mounts all 3 portals on a single public cloud URL with path-based routing:
- /admin        -> Super Admin Portal
- /             -> Consumer Developer Portal
- /api/calculator -> Calculator API
- /docs         -> Swagger UI
"""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.config import settings
from backend.app.init_db import init_db
from backend.app.routers.admin import router as admin_router
from backend.app.routers.consumer import router as consumer_router
from backend.app.routers.calculator import router as calculator_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="API Consumer Usage & Analytics Console",
    description="Unified API Provider & Consumer Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include All Routers
app.include_router(admin_router)
app.include_router(consumer_router)
app.include_router(calculator_router)

# Mount Admin Portal
FRONTEND_ADMIN_DIR = settings.BASE_DIR / "frontend" / "admin"
if FRONTEND_ADMIN_DIR.exists():
    app.mount("/admin-static", StaticFiles(directory=str(FRONTEND_ADMIN_DIR)), name="admin_static")

    @app.get("/admin")
    def serve_admin():
        return FileResponse(str(FRONTEND_ADMIN_DIR / "index.html"))

# Mount Consumer Portal
FRONTEND_CONSUMER_DIR = settings.BASE_DIR / "frontend" / "consumer"
if FRONTEND_CONSUMER_DIR.exists():
    app.mount("/consumer-static", StaticFiles(directory=str(FRONTEND_CONSUMER_DIR)), name="consumer_static")

    @app.get("/")
    def serve_consumer():
        return FileResponse(str(FRONTEND_CONSUMER_DIR / "index.html"))
