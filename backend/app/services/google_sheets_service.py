from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.refresh_handler import RefreshError
from google.api_python_client import discovery
import logging

from app.services.supabase_client import supabase

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    def __init__(self):
        self.sheets_service = None

    async def get_credentials(self):
        """Get fresh Google credentials from Supabase"""
        try:
            credentials_data = supabase.table("oauth_credentials").select("*").eq(
                "provider", "google_sheets"
            ).execute()

            if not credentials_data.data:
                raise Exception("Google Sheets not connected")

            cred = credentials_data.data[0]
            credentials = Credentials(
                token=cred["access_token"],
                refresh_token=cred["refresh_token"],
                token_uri="https://oauth2.googleapis.com/token",
                client_id="",  # Not needed for refresh
                client_secret="",
            )

            # Refresh if needed
            if credentials.expired:
                credentials.refresh(Request())
                # Update token in Supabase
                supabase.table("oauth_credentials").update({
                    "access_token": credentials.token,
                }).eq("provider", "google_sheets").execute()

            return credentials

        except Exception as e:
            logger.error(f"Error getting Google credentials: {str(e)}")
            raise

    async def get_contacts(self):
        """Get contacts from Google Sheets (Vārds, Telefona nr columns for Latvian sheets)"""
        try:
            credentials = await self.get_credentials()
            sheets = discovery.build("sheets", "v4", credentials=credentials)

            # Get spreadsheet ID from Supabase metadata
            metadata = supabase.table("oauth_credentials").select("metadata").eq(
                "provider", "google_sheets"
            ).execute()

            if not metadata.data or not metadata.data[0].get("metadata"):
                logger.error("No spreadsheet ID found")
                return []

            sheet_id = metadata.data[0]["metadata"].get("sheet_id")

            # Read all columns to find Name and Phone
            result = sheets.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range="Sheet1!A:Z",
            ).execute()

            values = result.get("values", [])
            if not values:
                return []

            # Find column indices for Name (Vārds) and Phone (Telefona nr)
            headers = values[0]
            name_col = None
            phone_col = None

            for idx, header in enumerate(headers):
                if "vārds" in header.lower() or "name" in header.lower():
                    name_col = idx
                if "telefona" in header.lower() or "phone" in header.lower():
                    phone_col = idx

            if name_col is None or phone_col is None:
                logger.error(f"Could not find Name or Phone columns. Headers: {headers}")
                return []

            contacts = []
            for row in values[1:]:  # Skip header
                if len(row) > max(name_col, phone_col):
                    name = row[name_col].strip() if name_col < len(row) else ""
                    phone = row[phone_col].strip() if phone_col < len(row) else ""
                    if name and phone:
                        contacts.append({
                            "name": name,
                            "phone": phone,
                        })

            logger.info(f"Retrieved {len(contacts)} contacts from Google Sheets")
            return contacts

        except Exception as e:
            logger.error(f"Error getting contacts: {str(e)}")
            raise
