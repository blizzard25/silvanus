# api/routes/oauth_routes.py
from fastapi import APIRouter, Request, HTTPException, Query, Depends
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from api.oauth.manager import OAUTH_PROVIDERS
from api.models.tokens import OAuthToken
from api.database import get_db
from api.polling import poll_all_tokens

router = APIRouter(tags=["OAuth"])

@router.get("/login/{provider}")
def oauth_login(
    provider: str,
    redirect_uri: Optional[str] = Query(default=None, description="Optional redirect URI"),
    user_id: Optional[str] = Query(default=None, description="Optional user identifier for session tracking")
):
    """
    Redirects the user to the third-party OAuth login page for the selected provider.
    Implements OAuth2.0 security best practices with PKCE and state parameters.
    """
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=404, 
            detail=f"Unsupported OAuth provider: {provider}. Supported providers: {list(OAUTH_PROVIDERS.keys())}"
        )

    try:
        auth_data = OAUTH_PROVIDERS[provider].get_auth_url(redirect_uri, user_id)
        return {
            "auth_url": auth_data["auth_url"],
            "state": auth_data["state"],
            "session_key": auth_data["session_key"],
            "provider": provider
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate authorization URL: {str(e)}")


@router.get("/callback/{provider}")
def oauth_callback(
    provider: str,
    code: str = Query(..., description="OAuth authorization code"),
    state: str = Query(..., description="OAuth state parameter for CSRF protection"),
    redirect_uri: Optional[str] = Query(default=None, description="OAuth redirect URI"),
    wallet_address: Optional[str] = Query(default=None, description="Optional wallet address to associate"),
    session_key: Optional[str] = Query(default=None, description="Session key for PKCE validation"),
    db: Session = Depends(get_db)
):
    """
    OAuth2.0 callback endpoint with comprehensive security validation.
    Validates state parameter, exchanges code with PKCE, and stores tokens securely.
    """
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=404, 
            detail=f"Unsupported OAuth provider: {provider}. Supported providers: {list(OAUTH_PROVIDERS.keys())}"
        )

    if not wallet_address:
        raise HTTPException(
            status_code=400, 
            detail="Missing required parameter: wallet_address"
        )

    try:
        tokens = OAUTH_PROVIDERS[provider].exchange_code(
            code=code,
            state=state,
            redirect_uri=redirect_uri,
            session_key=session_key
        )

        access_token = tokens.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=400, 
                detail="OAuth token exchange failed: missing access_token in response"
            )

        expires_in = tokens.get("expires_in", 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        token_entry = OAuthToken(
            wallet_address=wallet_address,
            provider=provider,
            access_token=access_token,
            refresh_token=tokens.get("refresh_token"),
            expires_at=expires_at
        )
        db.add(token_entry)
        db.commit()
        db.refresh(token_entry)

        return {
            "message": "OAuth authorization successful",
            "provider": provider,
            "wallet_address": wallet_address,
            "token_id": token_entry.id,
            "expires_in": expires_in,
            "expires_at": expires_at.isoformat(),
            "has_refresh_token": bool(tokens.get("refresh_token"))
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"OAuth validation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback processing failed: {str(e)}")

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

@router.get("/test/poll")
def test_polling():
    poll_all_tokens()
    return {"status": "Polling complete"}
