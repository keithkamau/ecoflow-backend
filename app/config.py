from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./waste_hub.db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Daraja M-Pesa API settings
    MPESA_CONSUMER_KEY: str = ""
    MPESA_CONSUMER_SECRET: str = ""
    MPESA_PASSKEY: str = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
    MPESA_SHORTCODE: str = "174379"
    MPESA_ENVIRONMENT: str = "sandbox"
    MPESA_CALLBACK_URL: str = "http://192.168.100.205:8000/api/v1/payments/callback"

    # Platform commission
    COMMISSION_RATE: float = 0.05

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
