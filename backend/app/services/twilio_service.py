import logging
import requests
import json
import re
from typing import List, Dict

from app.config import settings
from app.services.supabase_client import supabase

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_phone = settings.TWILIO_WHATSAPP_PHONE_NUMBER
        self.default_template_sid = settings.TWILIO_TEMPLATE_SID

        if not all([self.account_sid, self.auth_token, self.from_phone]):
            raise Exception("Twilio credentials not configured")

        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}"
        self.auth = (self.account_sid, self.auth_token)

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
        contact_name: str = None,
        twilio_template_sid: str = None,
        body: str = None,
    ) -> Dict:
        """Send a WhatsApp message via Twilio (template-based or free-form for testing)"""
        try:
            # Format phone number - clean and add + prefix
            phone_number = str(phone_number).strip()
            digits_only = re.sub(r'\D', '', phone_number)
            phone_number = '+' + digits_only

            # For free-form test messages
            if body:
                data = {
                    "From": f"whatsapp:{self.from_phone}",
                    "To": f"whatsapp:{phone_number}",
                    "Body": body,
                }
            else:
                # Use provided SID or fall back to default
                template_sid = twilio_template_sid or self.default_template_sid

                # Send using Twilio template with variable substitution
                # This allows sending outside the 24-hour messaging window
                data = {
                    "From": f"whatsapp:{self.from_phone}",
                    "To": f"whatsapp:{phone_number}",
                    "ContentSid": template_sid,
                    "ContentVariables": json.dumps({"1": contact_name}),
                }

            response = requests.post(
                f"{self.base_url}/Messages.json",
                data=data,
                auth=self.auth,
            )
            response.raise_for_status()
            result = response.json()
            message_sid = result.get("sid", "")

            logger.info(f"Message sent to {phone_number}: {message_sid}")

            return {
                "success": True,
                "message_sid": message_sid,
                "status": result.get("status", "queued"),
            }

        except Exception as e:
            logger.error(f"Error sending message to {phone_number}: {str(e)}")
            raise
