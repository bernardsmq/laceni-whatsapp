from fastapi import APIRouter, HTTPException
import logging

from app.services.supabase_client import supabase
from app.services.google_sheets_service import GoogleSheetsService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/contacts")
async def list_contacts():
    """List contacts synced from Google Sheets"""
    try:
        # Get from Supabase
        contacts = supabase.table("contacts").select("*").execute()
        return {"contacts": contacts.data or []}

    except Exception as e:
        logger.error(f"Error fetching contacts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-contacts")
async def sync_contacts():
    """Manually trigger sync from Google Sheets"""
    try:
        sheets_service = GoogleSheetsService()
        contacts = await sheets_service.sync_from_sheets()

        return {"success": True, "synced": len(contacts), "contacts": contacts}

    except Exception as e:
        logger.error(f"Error syncing contacts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
