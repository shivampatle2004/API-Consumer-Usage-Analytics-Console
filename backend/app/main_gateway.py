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


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Central Auth Gateway",
    description="Unified login gateway that dynamically routes users and admins to their portals.",
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


@app.post("/api/auth/login")
def unified_login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    redirect_url = settings.ADMIN_BASE_URL if user.role == UserRole.SUPER_ADMIN.value else settings.CONSUMER_BASE_URL

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username,
        "redirect_url": redirect_url
    }


# Serve Frontend static assets
FRONTEND_GATEWAY_DIR = settings.BASE_DIR / "frontend" / "gateway"
if FRONTEND_GATEWAY_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_GATEWAY_DIR)), name="gateway_static")

    @app.get("/")
    def serve_gateway_index():
        return FileResponse(str(FRONTEND_GATEWAY_DIR / "index.html"))

    @app.get("/{full_path:path}")
    def serve_gateway_files(full_path: str):
        target = FRONTEND_GATEWAY_DIR / full_path
        if target.is_file():
            return FileResponse(str(target))
        return FileResponse(str(FRONTEND_GATEWAY_DIR / "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main_gateway:app",
        host=settings.HOST,
        port=settings.GATEWAY_PORT,
        reload=False
    )
