import logging
from app.config import settings
from app.services.supabase_client import supabase

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    def __init__(self):
        self.sheet_id = settings.GOOGLE_SHEETS_ID

    async def get_contacts(self):
        """Get contacts from Supabase (synced from Google Sheets)"""
        try:
            if not self.sheet_id:
                logger.warning("No sheet ID configured (GOOGLE_SHEETS_ID env var)")
                return []

            # Fetch contacts from Supabase (they're synced separately)
            contacts = supabase.table("contacts").select("*").execute()
            contact_list = contacts.data or []

            logger.info(f"Retrieved {len(contact_list)} contacts from Supabase")
            return contact_list

        except Exception as e:
            logger.error(f"Error getting contacts: {str(e)}")
            return []
