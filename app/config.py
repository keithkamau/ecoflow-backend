from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./waste_hub.db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # AWS S3 (optional — falls back to local storage when not set)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = ""
    AWS_S3_REGION: str = "eu-west-1"
    STORAGE_BASE_URL: str = ""

    # Daraja M-Pesa API settings
    MPESA_CONSUMER_KEY: str = ""
    MPESA_CONSUMER_SECRET: str = ""
    MPESA_PASSKEY: str = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
    MPESA_SHORTCODE: str = "174379"
    MPESA_ENVIRONMENT: str = "sandbox"
    MPESA_CALLBACK_URL: str = "http://localhost:8000/api/v1/payments/callback"

    COMMISSION_RATE: float = 0.05

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
