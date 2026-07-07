from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio

from app.config import settings
from app.api import auth, templates, contacts, campaigns, logs
from app.services.google_sheets_service import GoogleSheetsService
from app.services.supabase_client import supabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sync_contacts_on_startup():
    """Sync contacts from Google Sheets on startup"""
    try:
        logger.info("Syncing contacts from Google Sheets on startup...")
        sheets_service = GoogleSheetsService()
        contact_list = await sheets_service.get_contacts()

        if contact_list:
            # Clear existing contacts
            supabase.table("contacts").delete().neq("id", "").execute()

            # Insert new contacts
            for contact in contact_list:
                supabase.table("contacts").insert({
                    "name": contact["name"],
                    "phone": contact["phone"],
                }).execute()

            logger.info(f"Synced {len(contact_list)} contacts from Google Sheets")
        else:
            logger.warning("No contacts found in Google Sheets")
    except Exception as e:
        logger.error(f"Error syncing contacts on startup: {str(e)}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Lāceni WhatsApp API")

    # Auto-sync contacts on startup if configured
    if settings.GOOGLE_SHEETS_ID:
        await sync_contacts_on_startup()

    yield
    logger.info("Shutting down Lāceni WhatsApp API")

app = FastAPI(
    title="Lāceni WhatsApp API",
    description="WhatsApp campaign management API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(templates.router, prefix="/api", tags=["templates"])
app.include_router(contacts.router, prefix="/api", tags=["contacts"])
app.include_router(campaigns.router, prefix="/api", tags=["campaigns"])
app.include_router(logs.router, prefix="/api", tags=["logs"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/status")
async def connection_status():
    """Check connection status for Meta and Google Sheets"""
    sheet_connected = bool(settings.GOOGLE_SHEETS_ID)
    return {
        "meta_connected": False,  # TODO: Check from Supabase
        "sheet_connected": sheet_connected,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
