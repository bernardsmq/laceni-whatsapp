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
        """Get contacts from Google Sheets (Name, Phone columns)"""
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

            # Read Name and Phone columns
            result = sheets.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range="Sheet1!A:B",
            ).execute()

            values = result.get("values", [])
            contacts = []

            for row in values[1:]:  # Skip header
                if len(row) >= 2:
                    contacts.append({
                        "name": row[0],
                        "phone": row[1],
                    })

            logger.info(f"Retrieved {len(contacts)} contacts from Google Sheets")
            return contacts

        except Exception as e:
            logger.error(f"Error getting contacts: {str(e)}")
            raise
