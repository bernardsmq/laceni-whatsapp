from supabase import create_client, Client
from app.config import settings

url = settings.get_supabase_url()
key = settings.get_service_role_key()

if not url or not key:
    raise RuntimeError("Supabase credentials not configured. Set NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(url, key)
