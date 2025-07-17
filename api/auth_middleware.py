from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.security import HTTPAuthorizationCredentials
from api.auth import get_current_user
from api.database import get_db

class AuthContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            db_gen = get_db()
            db = next(db_gen)
            
            api_key = request.headers.get("X-API-Key")
            auth_header = request.headers.get("Authorization")
            
            oauth_credentials = None
            if auth_header and auth_header.startswith("Bearer "):
                oauth_credentials = HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials=auth_header[7:]
                )
            
            user_context = await get_current_user(
                api_key=api_key,
                oauth_credentials=oauth_credentials,
                db=db
            )
            request.state.user = user_context
            
            db.close()
        except Exception:
            pass
        
        response = await call_next(request)
        return response
