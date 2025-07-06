# api/routes/oauth_routes.py
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import RedirectResponse
from typing import Optional
from api.oauth.manager import OAUTH_PROVIDERS

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

    # fallback handled inside get_auth_url()
    auth_url = OAUTH_PROVIDERS[provider].get_auth_url(redirect_uri)
    return {"auth_url": auth_url}


@router.get("/callback/{provider}")
def oauth_callback(provider: str, code: str = Query(...), redirect_uri: Optional[str] = None):
    """
    Handles the OAuth callback by exchanging the `code` for access tokens.
    """
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=404, detail="Unsupported OAuth provider")

    try:
        tokens = OAUTH_PROVIDERS[provider].exchange_code(code, redirect_uri)
        return {
            "provider": provider,
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "expires_in": tokens.get("expires_in"),
            "raw": tokens
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")
