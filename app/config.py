# app/config.py
import os

class Settings:
    APP_NAME = "EcoFlow API"
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecoflow_user:12345@localhost/ecoflow")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")

settings = Settings()
