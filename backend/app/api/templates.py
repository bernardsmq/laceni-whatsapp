from fastapi import APIRouter, HTTPException
import logging

from app.services.supabase_client import supabase
from app.services.twilio_service import TwilioService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/templates")
async def list_templates():
    """List available message templates from database"""
    try:
        twilio_service = TwilioService()
        templates = await twilio_service.get_message_templates()
        return {"templates": templates}

    except Exception as e:
        logger.error(f"Error fetching templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
