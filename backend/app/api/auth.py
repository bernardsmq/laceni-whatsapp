from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
import logging

from app.config import settings
from app.services.supabase_client import supabase

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/google-sheets")
async def google_sheets_auth():
    """Initiate Google Sheets OAuth flow"""
    from google_auth_oauthlib.flow import Flow

    flow = Flow.from_client_secrets_file(
        "credentials.json",  # Downloaded from Google Cloud Console
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )

    auth_url, state = flow.authorization_url(prompt="consent")
    return {"auth_url": auth_url, "state": state}

@router.get("/google-sheets/callback")
async def google_sheets_callback(code: str = Query(...), state: str = Query(...)):
    """Handle Google Sheets OAuth callback"""
    try:
        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_secrets_file(
            "credentials.json",
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
        )

        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Store credentials in Supabase
        supabase.table("oauth_credentials").insert({
            "provider": "google_sheets",
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_expiry": credentials.expiry.isoformat() if credentials.expiry else None,
        }).execute()

        logger.info("Google Sheets connected successfully")
        return RedirectResponse(url=f"{settings.FRONTEND_URL}?google_connected=true")

    except Exception as e:
        logger.error(f"Google Sheets auth error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/meta-whatsapp")
async def meta_whatsapp_auth():
    """Initiate Meta WhatsApp OAuth flow"""
    meta_auth_url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"  # Replace with actual Meta app ID
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"  # Replace with actual redirect URI
        f"scope=whatsapp_business_messaging,whatsapp_business_management"
    )
    return {"auth_url": meta_auth_url}

@router.get("/meta-whatsapp/callback")
async def meta_whatsapp_callback(code: str = Query(...)):
    """Handle Meta WhatsApp OAuth callback"""
    try:
        # Exchange code for access token
        # Store in Supabase
        logger.info("Meta WhatsApp connected successfully")
        return RedirectResponse(url=f"{settings.FRONTEND_URL}?meta_connected=true")

    except Exception as e:
        logger.error(f"Meta WhatsApp auth error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
