import logging
from typing import List, Dict
from twilio.rest import Client

from app.config import settings
from app.services.supabase_client import supabase

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_phone = settings.TWILIO_WHATSAPP_PHONE_NUMBER

        if not all([self.account_sid, self.auth_token, self.from_phone]):
            raise Exception("Twilio credentials not configured")

        self.client = Client(self.account_sid, self.auth_token)

    async def get_message_templates(self) -> List[Dict]:
        """Get message templates from Supabase (user-managed)"""
        try:
            templates = supabase.table("message_templates").select("*").execute()

            template_list = []
            for template in templates.data or []:
                template_list.append({
                    "id": template["template_id"],
                    "name": template["name"],
                    "body": template.get("body", ""),
                    "language": template.get("language", "en"),
                    "status": "approved",
                })

            logger.info(f"Retrieved {len(template_list)} templates from database")
            return template_list

        except Exception as e:
            logger.error(f"Error getting templates: {str(e)}")
            raise

    async def send_message(
        self,
        phone_number: str,
        template_id: str,
        body: str,
    ) -> Dict:
        """Send a WhatsApp message via Twilio"""
        try:
            # Format phone number (ensure it starts with +)
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number

            # Send message via Twilio WhatsApp
            message = self.client.messages.create(
                from_=f"whatsapp:{self.from_phone}",
                to=f"whatsapp:{phone_number}",
                body=body,
            )

            logger.info(f"Message sent to {phone_number}: {message.sid}")

            return {
                "success": True,
                "message_sid": message.sid,
                "status": message.status,
            }

        except Exception as e:
            logger.error(f"Error sending message to {phone_number}: {str(e)}")
            raise
