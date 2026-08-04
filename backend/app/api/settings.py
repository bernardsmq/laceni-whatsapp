from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from app.services.supabase_client import supabase

logger = logging.getLogger(__name__)
router = APIRouter()

class SettingsUpdate(BaseModel):
    meta_phone_id: str
    meta_access_token: str

@router.post("/settings")
async def save_settings(settings_data: SettingsUpdate):
    """Save Meta WhatsApp settings"""
    try:
        # Check if record exists
        existing = supabase.table("oauth_credentials").select("id").eq(
            "provider", "meta_whatsapp"
        ).execute()

        if existing.data:
            # Update existing
            supabase.table("oauth_credentials").update({
                "access_token": settings_data.meta_access_token,
                "metadata": {
                    "phone_id": settings_data.meta_phone_id,
                },
                "updated_at": "now()"
            }).eq("provider", "meta_whatsapp").execute()
            logger.info("Meta WhatsApp settings updated")
        else:
            # Insert new
            supabase.table("oauth_credentials").insert({
                "provider": "meta_whatsapp",
                "access_token": settings_data.meta_access_token,
                "metadata": {
                    "phone_id": settings_data.meta_phone_id,
                }
            }).execute()
            logger.info("Meta WhatsApp settings created")

        return {"success": True, "message": "Settings saved"}

    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/settings")
async def get_settings():
    """Get Meta WhatsApp settings"""
    try:
        result = supabase.table("oauth_credentials").select("*").eq(
            "provider", "meta_whatsapp"
        ).execute()

        if result.data:
            settings = result.data[0]
            return {
                "meta_connected": True,
                "phone_id": settings.get("metadata", {}).get("phone_id"),
            }
        else:
            return {"meta_connected": False}

    except Exception as e:
        logger.error(f"Error getting settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
