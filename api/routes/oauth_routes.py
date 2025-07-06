# api/routes/oauth_routes.py
from fastapi import APIRouter, Request, HTTPException, Query, Depends
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from api.oauth.manager import OAUTH_PROVIDERS
from api.models.tokens import OAuthToken
from api.database import get_db

router = APIRouter(tags=["OAuth"])

@router.get("/login/{provider}")
def oauth_login(
    provider: str,
    redirect_uri: Optional[str] = Query(default=None, description="Optional redirect URI")
):
    """
    Redirects the user to the third-party OAuth login page for the selected provider.
    """
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=404, detail="Unsupported OAuth provider")

    auth_url = OAUTH_PROVIDERS[provider].get_auth_url(redirect_uri)
    return {"auth_url": auth_url}


@router.get("/callback/{provider}")
def oauth_callback(
    provider: str,
    code: str = Query(..., description="OAuth authorization code"),
    redirect_uri: Optional[str] = None,
    wallet_address: Optional[str] = Query(default=None, description="Optional wallet address to associate"),
    db: Session = Depends(get_db)
):
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=404, detail="Unsupported OAuth provider")

    if not wallet_address:
        raise HTTPException(status_code=400, detail="Missing wallet_address")

    try:
        tokens = OAUTH_PROVIDERS[provider].exchange_code(code, redirect_uri)

        access_token = tokens.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="OAuth exchange failed: missing access token")

        # Store in DB
        token_entry = OAuthToken(
            wallet_address=wallet_address,
            provider=provider,
            access_token=access_token,
            refresh_token=tokens.get("refresh_token"),
            expires_at=datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3600))
        )
        db.add(token_entry)
        db.commit()

        return {
            "message": "OAuth success",
            "provider": provider,
            "wallet_address": wallet_address,
            "access_token": access_token,
            "refresh_token": tokens.get("refresh_token"),
            "expires_in": tokens.get("expires_in"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")

@router.post("/test/store-token")
def test_store_token(db: Session = Depends(get_db)):
    test_token = OAuthToken(
        wallet_address="0x123abc",
        provider="github",
        access_token="fake_access_token",
        refresh_token="fake_refresh_token",
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(test_token)
    db.commit()
    db.refresh(test_token)
    return {"status": "stored", "id": test_token.id}

@router.get("/test/list-tokens")
def list_tokens(db: Session = Depends(get_db)):
    return db.query(OAuthToken).all()