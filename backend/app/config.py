import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    BASE_DIR: Path = BASE_DIR
    DATABASE_URL: str = f"sqlite:///{DATA_DIR / 'app.db'}"
    SECRET_KEY: str = "super-secret-jwt-key-for-api-consumer-analytics-console-demo"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Ports
    GATEWAY_PORT: int = 8080
    ADMIN_PORT: int = 8100
    CALCULATOR_PORT: int = 8101
    CONSUMER_PORT: int = 8200
    HOST: str = "127.0.0.1"

    # Base URLs
    GATEWAY_BASE_URL: str = "http://localhost:8080"
    ADMIN_BASE_URL: str = "http://localhost:8100"
    CALCULATOR_BASE_URL: str = "http://localhost:8101"
    CONSUMER_BASE_URL: str = "http://localhost:8200"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        extra="ignore"
    )


settings = Settings()
