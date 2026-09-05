from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.app.config import settings
from backend.app.init_db import init_db
from backend.app.routers.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Super Admin Portal — API Provider Console",
    description="Portal for the API Provider to monitor consumers, API keys, usage, quota, and error rates.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Admin Router
app.include_router(admin_router)

# Serve Frontend static assets
FRONTEND_ADMIN_DIR = settings.BASE_DIR / "frontend" / "admin"
if FRONTEND_ADMIN_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_ADMIN_DIR)), name="admin_static")

    @app.get("/")
    def serve_admin_index():
        return FileResponse(str(FRONTEND_ADMIN_DIR / "index.html"))
    
    @app.get("/{full_path:path}")
    def serve_admin_files(full_path: str):
        target = FRONTEND_ADMIN_DIR / full_path
        if target.is_file():
            return FileResponse(str(target))
        return FileResponse(str(FRONTEND_ADMIN_DIR / "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main_admin:app",
        host=settings.HOST,
        port=settings.ADMIN_PORT,
        reload=False
    )
