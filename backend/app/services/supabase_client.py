from supabase import create_client, Client
from app.config import settings

url = settings.SUPABASE_URL
key = settings.SUPABASE_SERVICE_ROLE_KEY

supabase: Client = create_client(url, key)
