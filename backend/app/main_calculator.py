from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.init_db import init_db
from backend.app.routers.calculator import router as calculator_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Calculator API",
    description="The external API providing arithmetic operations (add, subtract, multiply, divide) secured via X-API-Key.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS so browser requests from Port 8200 / 8100 can hit the Calculator API seamlessly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Calculator Router
app.include_router(calculator_router)

@app.get("/")
def root():
    return {
        "service": "Calculator API",
        "status": "online",
        "documentation": f"{settings.CALCULATOR_BASE_URL}/docs",
        "endpoints": [
            f"{settings.CALCULATOR_BASE_URL}/api/calculator/add?a=10&b=20",
            f"{settings.CALCULATOR_BASE_URL}/api/calculator/subtract?a=20&b=10",
            f"{settings.CALCULATOR_BASE_URL}/api/calculator/multiply?a=5&b=6",
            f"{settings.CALCULATOR_BASE_URL}/api/calculator/divide?a=20&b=4"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main_calculator:app",
        host=settings.HOST,
        port=settings.CALCULATOR_PORT,
        reload=False
    )
