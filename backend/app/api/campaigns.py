from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from datetime import datetime

from app.services.supabase_client import supabase
from app.services.twilio_service import TwilioService

logger = logging.getLogger(__name__)
router = APIRouter()

class SendCampaignRequest(BaseModel):
    template_id: str

class SendTestRequest(BaseModel):
    phone_number: str
    message: str

@router.post("/campaigns/send-test")
async def send_test_message(request: SendTestRequest):
    """Send a test message to a specific phone number"""
    try:
        twilio_service = TwilioService()

        logger.info(f"Sending test message to {request.phone_number}")
        result = await twilio_service.send_message(
            phone_number=request.phone_number,
            template_id="test_message",
            body=request.message,
        )

        logger.info(f"Test message sent: {result}")
        return {
            "success": True,
            "message": f"Test message sent to {request.phone_number}",
            "result": result,
        }

    except Exception as e:
        logger.error(f"Error sending test message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/campaigns/send")
async def send_campaign(request: SendCampaignRequest):
    """Send a campaign to all contacts with personalized name"""
    try:
        # Get template
        template = supabase.table("message_templates").select("*").eq(
            "template_id", request.template_id
        ).execute()

        if not template.data:
            raise HTTPException(status_code=404, detail="Template not found")

        template_data = template.data[0]

        # Get all contacts
        contacts = supabase.table("contacts").select("*").execute()
        contact_list = contacts.data or []

        if not contact_list:
            raise HTTPException(status_code=400, detail="No contacts to send to")

        # Send messages via Meta WhatsApp API
        twilio_service = TwilioService()
        sent_count = 0
        failed_count = 0

        for contact in contact_list:
            try:
                twilio_sid = template_data.get("twilio_template_sid")

                await twilio_service.send_message(
                    phone_number=contact["phone"],
                    template_id=request.template_id,
                    contact_name=contact["name"],
                    twilio_template_sid=twilio_sid,
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send message to {contact['phone']}: {str(e)}")
                failed_count += 1

        # Log the campaign
        log_entry = {
            "template_id": request.template_id,
            "template_name": template_data["name"],
            "recipients_count": sent_count,
            "failed_count": failed_count,
            "status": "completed",
        }

        supabase.table("send_logs").insert(log_entry).execute()

        logger.info(f"Campaign sent: {sent_count} success, {failed_count} failed")

        return {
            "success": True,
            "sent": sent_count,
            "failed": failed_count,
            "total": len(contact_list),
        }

    except Exception as e:
        logger.error(f"Error sending campaign: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
