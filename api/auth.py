from fastapi import Header, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY_NAME = "X-API-Key"
API_KEYS = os.getenv("API_KEYS", "").split(",")
API_KEYS = [key.strip() for key in API_KEYS if key.strip()]

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")
