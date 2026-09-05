"""
Unified Production App for Free Cloud Deployment (Render / Railway / Fly.io)
Mounts all services on a single public cloud URL with path-based routing:
- /             -> Central Gateway Login (or Consumer Portal)
- /consumer     -> Consumer Developer Portal
- /admin        -> Super Admin Portal
- /api/...      -> All APIs (Calculator, Consumer, Admin, Auth)
- /docs         -> Swagger UI
"""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.init_db import init_db
from backend.app.database import get_db
from backend.app.models import User, UserRole
from backend.app.auth import verify_password, create_access_token
from backend.app.schemas import LoginRequest
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


@app.post("/api/auth/login")
def unified_login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    redirect_url = "/admin" if user.role == UserRole.SUPER_ADMIN.value else "/consumer"

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username,
        "redirect_url": redirect_url
    }


# Static File Directories
FRONTEND_GATEWAY_DIR = settings.BASE_DIR / "frontend" / "gateway"
FRONTEND_ADMIN_DIR = settings.BASE_DIR / "frontend" / "admin"
FRONTEND_CONSUMER_DIR = settings.BASE_DIR / "frontend" / "consumer"

# 1. Central Gateway Routes
@app.get("/")
def serve_gateway_index():
    return FileResponse(str(FRONTEND_GATEWAY_DIR / "index.html"))

@app.get("/gateway")
def serve_gateway():
    return FileResponse(str(FRONTEND_GATEWAY_DIR / "index.html"))

@app.get("/gateway/style.css")
def serve_gateway_css():
    return FileResponse(str(FRONTEND_GATEWAY_DIR / "style.css"), media_type="text/css")

@app.get("/gateway/app.js")
def serve_gateway_js():
    return FileResponse(str(FRONTEND_GATEWAY_DIR / "app.js"), media_type="application/javascript")


# 2. Consumer Portal Routes
@app.get("/consumer")
def serve_consumer():
    return FileResponse(str(FRONTEND_CONSUMER_DIR / "index.html"))

@app.get("/consumer/style.css")
@app.get("/style.css")
def serve_consumer_css():
    return FileResponse(str(FRONTEND_CONSUMER_DIR / "style.css"), media_type="text/css")

@app.get("/consumer/app.js")
@app.get("/app.js")
def serve_consumer_js():
    return FileResponse(str(FRONTEND_CONSUMER_DIR / "app.js"), media_type="application/javascript")


# 3. Admin Portal Routes
@app.get("/admin")
def serve_admin():
    return FileResponse(str(FRONTEND_ADMIN_DIR / "index.html"))

@app.get("/admin/style.css")
def serve_admin_css():
    return FileResponse(str(FRONTEND_ADMIN_DIR / "style.css"), media_type="text/css")

@app.get("/admin/app.js")
def serve_admin_js():
    return FileResponse(str(FRONTEND_ADMIN_DIR / "app.js"), media_type="application/javascript")
