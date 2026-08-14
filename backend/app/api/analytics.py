from fastapi import APIRouter, HTTPException
import logging
from app.services.supabase_client import supabase

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/analytics/campaign-stats")
async def get_campaign_stats(template_id: str = None):
    """Get message delivery stats for a campaign or all messages"""
    try:
        query = supabase.table("message_status").select("*")

        if template_id:
            query = query.eq("template_id", template_id)

        result = query.execute()
        messages = result.data or []

        # Calculate stats
        stats = {
            "total": len(messages),
            "queued": len([m for m in messages if m["status"] == "queued"]),
            "sent": len([m for m in messages if m["status"] == "sent"]),
            "delivered": len([m for m in messages if m["status"] == "delivered"]),
            "read": len([m for m in messages if m["status"] == "read"]),
            "failed": len([m for m in messages if m["status"] == "failed"]),
        }

        return {
            "success": True,
            "stats": stats,
            "template_id": template_id or "all",
        }

    except Exception as e:
        logger.error(f"Error fetching campaign stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/message-status/{message_sid}")
async def get_message_status(message_sid: str):
    """Get status for a specific message"""
    try:
        result = supabase.table("message_status").select("*").eq(
            "message_sid", message_sid
        ).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Message not found")

        message = result.data[0]
        return {
            "success": True,
            "message": message,
        }

    except Exception as e:
        logger.error(f"Error fetching message status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/all-messages")
async def get_all_messages(template_id: str = None, status: str = None):
    """Get all messages with optional filtering"""
    try:
        query = supabase.table("message_status").select("*")

        if template_id:
            query = query.eq("template_id", template_id)

        if status:
            query = query.eq("status", status)

        result = query.order("created_at", desc=True).execute()
        messages = result.data or []

        return {
            "success": True,
            "count": len(messages),
            "messages": messages,
        }

    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
