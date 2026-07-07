import logging
import httpx
import json
import time
from google.auth import _helpers
from google.oauth2 import service_account
from app.config import settings, get_service_account_credentials
from app.services.supabase_client import supabase

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    def __init__(self):
        self.sheet_id = settings.GOOGLE_SHEETS_ID

    async def _get_access_token(self):
        """Get access token from service account"""
        try:
            from google.auth.transport.requests import Request

            creds_dict = get_service_account_credentials()
            if not creds_dict:
                raise Exception("No credentials")

            credentials = service_account.Credentials.from_service_account_info(
                creds_dict,
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
            )

            # Refresh credentials to get access token
            request = Request()
            credentials.refresh(request)

            logger.info(f"Got access token: {credentials.token[:20]}...")
            return credentials.token

        except Exception as e:
            logger.error(f"Failed to get access token: {str(e)}")
            raise

    async def sync_from_sheets(self):
        """Sync contacts from Google Sheets to Supabase"""
        try:
            if not self.sheet_id:
                logger.error("No sheet ID configured")
                return []

            logger.info(f"Starting sync from sheet {self.sheet_id}")

            # Get access token
            access_token = await self._get_access_token()
            logger.info("Got access token")

            # Call Google Sheets API
            async with httpx.AsyncClient() as client:
                url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.sheet_id}/values/Sheet1!A:Z"
                headers = {"Authorization": f"Bearer {access_token}"}

                response = await client.get(url, headers=headers)

                if response.status_code != 200:
                    logger.error(f"Google Sheets API error {response.status_code}: {response.text}")
                    return []

                data = response.json()
                values = data.get("values", [])

                logger.info(f"Got {len(values)} rows from sheet")

                if not values or len(values) < 2:
                    logger.warning("No data in sheet or only headers")
                    return []

                # Find columns
                headers = values[0]
                logger.info(f"Headers: {headers}")

                name_col = None
                phone_col = None

                for idx, header in enumerate(headers):
                    h_lower = header.lower() if header else ""
                    if "vārds" in h_lower or "name" in h_lower:
                        name_col = idx
                        logger.info(f"Found name column at index {idx}: {header}")
                    if "telefona" in h_lower or "phone" in h_lower:
                        phone_col = idx
                        logger.info(f"Found phone column at index {idx}: {header}")

                if name_col is None or phone_col is None:
                    logger.error(f"Missing columns. Name col: {name_col}, Phone col: {phone_col}")
                    return []

                # Extract contacts
                contacts = []
                for i, row in enumerate(values[1:], start=2):
                    try:
                        name = row[name_col].strip() if name_col < len(row) and row[name_col] else ""
                        phone = row[phone_col].strip() if phone_col < len(row) and row[phone_col] else ""

                        if name and phone:
                            contacts.append({"name": name, "phone": phone})
                            logger.info(f"Row {i}: {name}, {phone}")
                    except Exception as e:
                        logger.warning(f"Row {i} error: {str(e)}")
                        continue

                logger.info(f"Extracted {len(contacts)} contacts")

                # Clear old contacts and insert new ones
                try:
                    # Delete all contacts - get all first then delete by id
                    existing = supabase.table("contacts").select("id").execute()
                    for row in existing.data or []:
                        supabase.table("contacts").delete().eq("id", row["id"]).execute()
                except Exception as e:
                    logger.warning(f"Could not delete old contacts: {str(e)}")

                # Insert new contacts
                for contact in contacts:
                    supabase.table("contacts").insert({
                        "name": contact["name"],
                        "phone": contact["phone"],
                    }).execute()

                logger.info(f"Synced {len(contacts)} contacts to Supabase")
                return contacts

        except Exception as e:
            logger.error(f"Error syncing from sheets: {str(e)}", exc_info=True)
            return []

    async def get_contacts(self):
        """Get contacts from Supabase"""
        try:
            contacts = supabase.table("contacts").select("*").execute()
            return contacts.data or []
        except Exception as e:
            logger.error(f"Error getting contacts: {str(e)}")
            return []
