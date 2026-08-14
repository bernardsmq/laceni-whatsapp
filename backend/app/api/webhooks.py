from fastapi import APIRouter, Request, HTTPException
import logging
from app.services.twilio_service import TwilioService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/webhooks/twilio")
async def twilio_webhook(request: Request):
    """
    Receive delivery and read status updates from Twilio
    Twilio sends: MessageSid, MessageStatus (queued, sent, delivered, read, failed)
    """
    try:
        form_data = await request.form()
        message_sid = form_data.get("MessageSid")
        message_status = form_data.get("MessageStatus")
        error_code = form_data.get("ErrorCode")

        if not message_sid or not message_status:
            logger.warning(f"Invalid webhook payload: {form_data}")
            raise HTTPException(status_code=400, detail="Missing MessageSid or MessageStatus")

        logger.info(f"Webhook received: {message_sid} -> {message_status}")

        # Update message status in database
        twilio_service = TwilioService()
        await twilio_service.update_message_status(
            message_sid=message_sid,
            status=message_status,
            error_code=error_code,
        )

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
