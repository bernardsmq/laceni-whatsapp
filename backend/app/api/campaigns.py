from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from datetime import datetime

from app.services.supabase_client import supabase
from app.services.meta_service import MetaService

logger = logging.getLogger(__name__)
router = APIRouter()

class SendCampaignRequest(BaseModel):
    template_id: str

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
        meta_service = MetaService()
        sent_count = 0
        failed_count = 0

        for contact in contact_list:
            try:
                # Personalize message with contact's name
                message_body = template_data["body"].replace("{{name}}", contact["name"])

                await meta_service.send_message(
                    phone_number=contact["phone"],
                    template_id=request.template_id,
                    body=message_body,
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send message to {contact['phone']}: {str(e)}")
                failed_count += 1

        # Log the campaign
        log_entry = {
            "sent_at": datetime.utcnow().isoformat(),
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
        logger.error(f"Error sending campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
