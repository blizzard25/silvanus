from fastapi import Header, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from enum import Enum
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from api.models.tokens import OAuthToken
from api.database import get_db

load_dotenv()

API_KEY_NAME = "X-API-Key"
API_KEYS = os.getenv("API_KEYS", "").split(",")
API_KEYS = [key.strip() for key in API_KEYS if key.strip()]

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
oauth2_scheme = HTTPBearer(auto_error=False)

class APIKeyTier(Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    ADMIN = "admin"

class AuthMethod(Enum):
    API_KEY = "api_key"
    OAUTH2 = "oauth2"

class OAuthScope(Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

def get_api_key_tier(api_key: str) -> APIKeyTier:
    """Determine API key tier based on key pattern or configuration"""
    if not api_key:
        return APIKeyTier.BASIC
    
    if len(api_key) > 20 or 'admin' in api_key.lower():
        return APIKeyTier.ADMIN
    
    if len(api_key) > 15 and re.search(r'\d', api_key) and re.search(r'[a-zA-Z]', api_key):
        return APIKeyTier.PREMIUM
    
    return APIKeyTier.BASIC

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")
    return api_key

async def get_api_key_with_tier(api_key: str = Security(api_key_header)):
    if api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")
    tier = get_api_key_tier(api_key)
    return {"key": api_key, "tier": tier, "auth_method": AuthMethod.API_KEY}

async def validate_oauth_token(
    credentials: HTTPAuthorizationCredentials = Security(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Validate OAuth2.0 bearer token and return user context"""
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing OAuth2.0 bearer token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    
    oauth_token = db.query(OAuthToken).filter(
        OAuthToken.access_token == token,
        OAuthToken.expires_at > datetime.utcnow()
    ).first()
    
    if not oauth_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired OAuth2.0 token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return {
        "wallet_address": oauth_token.wallet_address,
        "provider": oauth_token.provider,
        "token_id": oauth_token.id,
        "auth_method": AuthMethod.OAUTH2,
        "scopes": [OAuthScope.READ, OAuthScope.WRITE]
    }

async def refresh_oauth_token(
    token_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Refresh an expired OAuth2.0 token using refresh token"""
    oauth_token = db.query(OAuthToken).filter(OAuthToken.id == token_id).first()
    
    if not oauth_token or not oauth_token.refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Token refresh not available"
        )
    
    from api.oauth.manager import OAUTH_PROVIDERS
    
    if oauth_token.provider not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=500,
            detail=f"OAuth provider {oauth_token.provider} not available"
        )
    
    try:
        provider = OAUTH_PROVIDERS[oauth_token.provider]
        new_tokens = provider.refresh_token(oauth_token.refresh_token)
        
        oauth_token.access_token = new_tokens["access_token"]
        oauth_token.expires_at = datetime.utcnow() + timedelta(seconds=new_tokens.get("expires_in", 3600))
        
        if "refresh_token" in new_tokens:
            oauth_token.refresh_token = new_tokens["refresh_token"]
        
        db.commit()
        db.refresh(oauth_token)
        
        return {
            "access_token": oauth_token.access_token,
            "expires_in": new_tokens.get("expires_in", 3600),
            "token_type": "bearer"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Token refresh failed: {str(e)}"
        )

async def get_current_user(
    api_key: Optional[str] = Security(api_key_header),
    oauth_credentials: Optional[HTTPAuthorizationCredentials] = Security(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Unified authentication supporting both API keys and OAuth2.0 tokens"""
    
    if oauth_credentials:
        return await validate_oauth_token(oauth_credentials, db)
    
    elif api_key:
        if api_key not in API_KEYS:
            raise HTTPException(status_code=403, detail="Invalid API Key")
        
        tier = get_api_key_tier(api_key)
        return {
            "api_key": api_key,
            "tier": tier,
            "auth_method": AuthMethod.API_KEY,
            "scopes": [OAuthScope.READ, OAuthScope.WRITE, OAuthScope.ADMIN] if tier == APIKeyTier.ADMIN else [OAuthScope.READ, OAuthScope.WRITE]
        }
    
    else:
        raise HTTPException(
            status_code=401,
            detail="Authentication required: provide either API key or OAuth2.0 bearer token",
            headers={"WWW-Authenticate": "Bearer"}
        )

def require_scope(required_scope: OAuthScope):
    """Decorator to require specific OAuth2.0 scope"""
    def scope_dependency(user: Dict[str, Any] = Depends(get_current_user)):
        user_scopes = user.get("scopes", [])
        if required_scope not in user_scopes:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions: {required_scope.value} scope required"
            )
        return user
    return scope_dependency
