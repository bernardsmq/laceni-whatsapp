from fastapi import APIRouter, HTTPException
import logging

from app.services.supabase_client import supabase
from app.services.meta_service import MetaService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/templates")
async def list_templates():
    """List available message templates from Meta WhatsApp"""
    try:
        # Get credentials from Supabase
        credentials = supabase.table("oauth_credentials").select("*").eq(
            "provider", "meta_whatsapp"
        ).execute()

        if not credentials.data:
            return {"templates": []}

        meta_service = MetaService()
        templates = await meta_service.get_message_templates()

        # Store templates in Supabase for quick access
        for template in templates:
            supabase.table("message_templates").upsert({
                "template_id": template["id"],
                "name": template["name"],
                "body": template.get("body", ""),
                "language": template.get("language", "en"),
            }).execute()

        return {"templates": templates}

    except Exception as e:
        logger.error(f"Error fetching templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
