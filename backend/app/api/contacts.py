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
        # Get Google Sheets credentials
        credentials = supabase.table("oauth_credentials").select("*").eq(
            "provider", "google_sheets"
        ).execute()

        if not credentials.data:
            raise HTTPException(status_code=400, detail="Google Sheets not connected")

        sheets_service = GoogleSheetsService()
        contacts = await sheets_service.get_contacts()

        # Clear and re-insert contacts
        supabase.table("contacts").delete().neq("id", "").execute()

        for contact in contacts:
            supabase.table("contacts").insert({
                "name": contact["name"],
                "phone": contact["phone"],
            }).execute()

        logger.info(f"Synced {len(contacts)} contacts from Google Sheets")
        return {"synced": len(contacts), "contacts": contacts}

    except Exception as e:
        logger.error(f"Error syncing contacts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
