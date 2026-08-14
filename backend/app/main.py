from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api import auth, templates, contacts, campaigns, logs, settings as settings_api, webhooks, analytics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Lāceni WhatsApp API")
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
app.include_router(settings_api.router, prefix="/api", tags=["settings"])
app.include_router(webhooks.router, prefix="/api", tags=["webhooks"])
app.include_router(analytics.router, prefix="/api", tags=["analytics"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/status")
async def connection_status():
    """Check connection status for Twilio and Google Sheets"""
    twilio_connected = bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_WHATSAPP_PHONE_NUMBER)
    sheet_connected = bool(settings.GOOGLE_SHEETS_ID)

    return {
        "meta_connected": twilio_connected,  # Keep 'meta_connected' key for frontend compatibility
        "sheet_connected": sheet_connected,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
