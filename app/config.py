# app/config.py
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "EcoFlow Backend"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite:///./ecoflow.db"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()
