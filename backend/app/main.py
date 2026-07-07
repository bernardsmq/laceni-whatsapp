from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api import auth, templates, contacts, campaigns, logs

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

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/status")
async def connection_status():
    """Check connection status for Meta and Google Sheets"""
    return {
        "meta_connected": False,  # TODO: Check from Supabase
        "sheet_connected": False,  # TODO: Check from Supabase
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
