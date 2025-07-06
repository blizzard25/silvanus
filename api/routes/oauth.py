# routes/oauth.py
from fastapi import APIRouter, Request, HTTPException
from oauth.manager import OAUTH_PROVIDERS

router = APIRouter(tags=["oauth"])

@router.get("/oauth/login/{provider}")
def oauth_login(provider: str, redirect_uri: str):
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=404, detail="Unsupported provider")
    url = OAUTH_PROVIDERS[provider].get_auth_url(redirect_uri)
    return {"auth_url": url}

@router.get("/oauth/callback/{provider}")
def oauth_callback(provider: str, code: str, redirect_uri: str):
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=404, detail="Unsupported provider")
    tokens = OAUTH_PROVIDERS[provider].exchange_code(code, redirect_uri)
    return {"provider": provider, "tokens": tokens}
