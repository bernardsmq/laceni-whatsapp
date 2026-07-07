import logging
import httpx
import json
from google.oauth2 import service_account
from app.config import settings, get_service_account_credentials
from app.services.supabase_client import supabase

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    def __init__(self):
        self.sheet_id = settings.GOOGLE_SHEETS_ID

    async def sync_from_sheets(self):
        """Sync contacts from Google Sheets to Supabase"""
        try:
            if not self.sheet_id:
                logger.warning("No sheet ID configured")
                return []

            # Get service account credentials
            creds_dict = get_service_account_credentials()
            if not creds_dict:
                logger.error("No service account credentials")
                return []

            # Get access token
            credentials = service_account.Credentials.from_service_account_info(
                creds_dict,
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
            )

            # Refresh to get access token
            request = httpx.Request("GET", "https://www.google.com")
            credentials.refresh(request)
            access_token = credentials.token

            # Call Google Sheets API
            async with httpx.AsyncClient() as client:
                url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.sheet_id}/values/Sheet1!A:Z"
                response = await client.get(
                    url,
                    params={"access_token": access_token}
                )

                if response.status_code != 200:
                    logger.error(f"Google Sheets API error: {response.text}")
                    return []

                data = response.json()
                values = data.get("values", [])

                if not values or len(values) < 2:
                    logger.warning("No data in sheet")
                    return []

                # Find columns
                headers = values[0]
                name_col = None
                phone_col = None

                for idx, header in enumerate(headers):
                    if "vārds" in header.lower() or "name" in header.lower():
                        name_col = idx
                    if "telefona" in header.lower() or "phone" in header.lower():
                        phone_col = idx

                if name_col is None or phone_col is None:
                    logger.error(f"Missing Name or Phone columns. Headers: {headers}")
                    return []

                # Extract contacts
                contacts = []
                for row in values[1:]:
                    if len(row) > max(name_col, phone_col):
                        name = row[name_col].strip() if name_col < len(row) else ""
                        phone = row[phone_col].strip() if phone_col < len(row) else ""
                        if name and phone:
                            contacts.append({"name": name, "phone": phone})

                # Clear and sync to Supabase
                supabase.table("contacts").delete().neq("id", "").execute()
                for contact in contacts:
                    supabase.table("contacts").insert({
                        "name": contact["name"],
                        "phone": contact["phone"],
                    }).execute()

                logger.info(f"Synced {len(contacts)} contacts from Google Sheets")
                return contacts

        except Exception as e:
            logger.error(f"Error syncing from sheets: {str(e)}")
            return []

    async def get_contacts(self):
        """Get contacts from Supabase"""
        try:
            contacts = supabase.table("contacts").select("*").execute()
            return contacts.data or []
        except Exception as e:
            logger.error(f"Error getting contacts: {str(e)}")
            return []
