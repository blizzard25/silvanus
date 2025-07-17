from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Dict, Any

def get_user_identity(request: Request) -> str:
    """Get user identity for rate limiting from OAuth2.0 token or API key"""
    user_context = getattr(request.state, 'user', None)
    
    if user_context:
        if user_context.get('auth_method') == 'oauth2':
            return f"oauth2:{user_context.get('wallet_address', 'unknown')}"
        elif user_context.get('auth_method') == 'api_key':
            return f"api_key:{user_context.get('api_key', 'unknown')}"
    
    return f"ip:{get_remote_address(request)}"

limiter = Limiter(key_func=get_user_identity)
