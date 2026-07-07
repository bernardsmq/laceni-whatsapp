from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import logging
import csv
import io
from datetime import datetime

from app.services.supabase_client import supabase

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/logs")
async def get_logs():
    """Get send logs and tracking stats"""
    try:
        logs = supabase.table("send_logs").select("*").order(
            "sent_at", desc=True
        ).execute()

        log_data = logs.data or []

        # Calculate stats
        stats = {
            "sent": sum(log.get("recipients_count", 0) for log in log_data),
            "delivered": sum(
                log.get("delivered_count", 0) for log in log_data if log.get("status") == "delivered"
            ),
            "read": sum(log.get("read_count", 0) for log in log_data if log.get("status") == "read"),
        }

        return {
            "stats": stats,
            "logs": log_data,
        }

    except Exception as e:
        logger.error(f"Error fetching logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/export")
async def export_logs():
    """Export send logs as CSV"""
    try:
        logs = supabase.table("send_logs").select("*").order(
            "sent_at", desc=True
        ).execute()

        log_data = logs.data or []

        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Sent At", "Template", "Recipients", "Status", "Delivered", "Read"])

        for log in log_data:
            writer.writerow([
                log.get("sent_at", ""),
                log.get("template_name", ""),
                log.get("recipients_count", 0),
                log.get("status", ""),
                log.get("delivered_count", 0),
                log.get("read_count", 0),
            ])

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=logs.csv"},
        )

    except Exception as e:
        logger.error(f"Error exporting logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
