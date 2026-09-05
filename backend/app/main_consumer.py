from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.app.config import settings
from backend.app.init_db import init_db
from backend.app.routers.consumer import router as consumer_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="API Consumer / Developer Portal",
    description="Developer console for API consumers to explore APIs, copy API keys, test endpoints, and view analytics.",
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

# Include Consumer Router
app.include_router(consumer_router)

# Serve Frontend static assets
FRONTEND_CONSUMER_DIR = settings.BASE_DIR / "frontend" / "consumer"
if FRONTEND_CONSUMER_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_CONSUMER_DIR)), name="consumer_static")

    @app.get("/")
    def serve_consumer_index():
        return FileResponse(str(FRONTEND_CONSUMER_DIR / "index.html"))
    
    @app.get("/{full_path:path}")
    def serve_consumer_files(full_path: str):
        target = FRONTEND_CONSUMER_DIR / full_path
        if target.is_file():
            return FileResponse(str(target))
        return FileResponse(str(FRONTEND_CONSUMER_DIR / "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main_consumer:app",
        host=settings.HOST,
        port=settings.CONSUMER_PORT,
        reload=False
    )
