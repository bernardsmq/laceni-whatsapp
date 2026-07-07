from pydantic_settings import BaseSettings
from typing import Optional
import json

class Settings(BaseSettings):
    # Supabase (use NEXT_PUBLIC_SUPABASE_URL if SUPABASE_URL not set)
    SUPABASE_URL: Optional[str] = None
    NEXT_PUBLIC_SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None

    def get_supabase_url(self) -> str:
        return self.SUPABASE_URL or self.NEXT_PUBLIC_SUPABASE_URL or ""

    def get_service_role_key(self) -> str:
        return self.SUPABASE_SERVICE_ROLE_KEY or self.SUPABASE_KEY or ""

    # Google Service Account (for direct Sheets access)
    GOOGLE_SERVICE_ACCOUNT_JSON: Optional[str] = None
    GOOGLE_SHEETS_ID: Optional[str] = None

    # Google OAuth (legacy, can be removed)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None

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

# Parse service account JSON if provided
def get_service_account_credentials():
    """Parse service account JSON from environment"""
    if not settings.GOOGLE_SERVICE_ACCOUNT_JSON:
        return None
    try:
        return json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON)
    except json.JSONDecodeError:
        return None
