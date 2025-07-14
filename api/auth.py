from fastapi import Header, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
import os
from dotenv import load_dotenv
from enum import Enum
import re

load_dotenv()

API_KEY_NAME = "X-API-Key"
API_KEYS = os.getenv("API_KEYS", "").split(",")
API_KEYS = [key.strip() for key in API_KEYS if key.strip()]

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

class APIKeyTier(Enum):
    BASIC = "basic"
    PREMIUM = "premium"
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
    return {"key": api_key, "tier": tier}
