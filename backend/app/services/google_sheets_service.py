from google.oauth2 import service_account
from google.api_python_client import discovery
import logging
from app.config import settings, get_service_account_credentials
from app.services.supabase_client import supabase

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    def __init__(self):
        self.sheets_service = None
        self.sheet_id = settings.GOOGLE_SHEETS_ID

    async def get_credentials(self):
        """Get service account credentials for Google Sheets"""
        try:
            creds_dict = get_service_account_credentials()
            if not creds_dict:
                raise Exception("Google service account credentials not configured")

            credentials = service_account.Credentials.from_service_account_info(
                creds_dict,
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
            )
            return credentials

        except Exception as e:
            logger.error(f"Error getting Google credentials: {str(e)}")
            raise

    async def get_contacts(self):
        """Get contacts from Google Sheets (Vārds, Telefona nr columns for Latvian sheets)"""
        try:
            if not self.sheet_id:
                logger.error("No sheet ID configured (GOOGLE_SHEETS_ID env var)")
                return []

            credentials = await self.get_credentials()
            sheets = discovery.build("sheets", "v4", credentials=credentials)

            # Read all columns to find Name and Phone
            result = sheets.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range="Sheet1!A:Z",
            ).execute()

            values = result.get("values", [])
            if not values or len(values) < 2:
                logger.warning("No data found in sheet or sheet is empty")
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
