from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    # Meta WhatsApp
    META_BUSINESS_ACCOUNT_ID: Optional[str] = None
    META_WHATSAPP_BUSINESS_ACCOUNT_ID: Optional[str] = None
    META_PHONE_NUMBER_ID: Optional[str] = None

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Environment
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "your-secret-key-change-in-production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
