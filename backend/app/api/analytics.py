from fastapi import APIRouter, HTTPException
import logging
from datetime import datetime, timedelta
from app.services.supabase_client import supabase

logger = logging.getLogger(__name__)
router = APIRouter()

def _apply_date_filter(query, date_from: str = None, date_to: str = None):
    """Apply date filtering to a query"""
    if date_from:
        query = query.gte("created_at", date_from)
    if date_to:
        query = query.lte("created_at", date_to)
    return query

@router.get("/analytics/campaign-stats")
async def get_campaign_stats(template_id: str = None, date_from: str = None, date_to: str = None):
    """Get message delivery stats for a campaign or all messages with optional date filtering"""
    try:
        query = supabase.table("message_status").select("*")

        if template_id:
            query = query.eq("template_id", template_id)

        query = _apply_date_filter(query, date_from, date_to)

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
async def get_all_messages(template_id: str = None, status: str = None, date_from: str = None, date_to: str = None):
    """Get all messages with optional filtering (template, status, date range)"""
    try:
        query = supabase.table("message_status").select("*")

        if template_id:
            query = query.eq("template_id", template_id)

        if status:
            query = query.eq("status", status)

        query = _apply_date_filter(query, date_from, date_to)

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
