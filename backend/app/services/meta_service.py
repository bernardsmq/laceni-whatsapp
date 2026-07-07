import requests
import logging
from typing import List, Dict

from app.config import settings
from app.services.supabase_client import supabase

logger = logging.getLogger(__name__)

class MetaService:
    BASE_URL = "https://graph.instagram.com/v18.0"

    def __init__(self):
        self.access_token = self._get_access_token()

    def _get_access_token(self) -> str:
        """Get Meta access token from Supabase"""
        try:
            cred_data = supabase.table("oauth_credentials").select("*").eq(
                "provider", "meta_whatsapp"
            ).execute()

            if not cred_data.data:
                raise Exception("Meta WhatsApp not connected")

            return cred_data.data[0]["access_token"]

        except Exception as e:
            logger.error(f"Error getting Meta access token: {str(e)}")
            raise

    async def get_message_templates(self) -> List[Dict]:
        """Get message templates from Meta WhatsApp Business account"""
        try:
            url = f"{self.BASE_URL}/{settings.META_WHATSAPP_BUSINESS_ACCOUNT_ID}/message_templates"
            params = {"access_token": self.access_token}

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            templates = []

            for template in data.get("data", []):
                templates.append({
                    "id": template["id"],
                    "name": template["name"],
                    "body": template.get("components", [{}])[0].get("text", ""),
                    "language": template.get("language", "en"),
                    "status": template.get("status", ""),
                })

            logger.info(f"Retrieved {len(templates)} templates from Meta")
            return templates

        except Exception as e:
            logger.error(f"Error getting templates: {str(e)}")
            raise

    async def send_message(
        self,
        phone_number: str,
        template_id: str,
        body: str,
    ) -> Dict:
        """Send a message via WhatsApp API"""
        try:
            # Format phone number (remove non-digits)
            clean_phone = "".join(c for c in phone_number if c.isdigit())

            url = f"{self.BASE_URL}/{settings.META_PHONE_NUMBER_ID}/messages"
            headers = {"Authorization": f"Bearer {self.access_token}"}

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": clean_phone,
                "type": "template",
                "template": {
                    "name": template_id,
                    "language": {
                        "code": "en_US",
                    },
                    "body": {
                        "parameters": [
                            {
                                "type": "text",
                                "text": body,
                            }
                        ]
                    },
                },
            }

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Message sent to {phone_number}: {result.get('messages', [{}])[0].get('id')}")

            return result

        except Exception as e:
            logger.error(f"Error sending message to {phone_number}: {str(e)}")
            raise
