from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import json

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_request_size: int = 1024 * 1024):
        super().__init__(app)
        self.max_request_size = max_request_size
    
    async def dispatch(self, request: Request, call_next):
        if request.headers.get('content-length'):
            content_length = int(request.headers['content-length'])
            if content_length > self.max_request_size:
                raise HTTPException(status_code=413, detail="Request too large")
        
        if request.headers.get('content-type') == 'application/json':
            try:
                body = await request.body()
                if body:
                    data = json.loads(body)
                    sanitized_data = self._sanitize_payload(data)
                    
                    request._body = json.dumps(sanitized_data).encode()
            except (json.JSONDecodeError, UnicodeDecodeError):
                raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        response = await call_next(request)
        return response
    
    def _sanitize_payload(self, data):
        """Sanitize payload data"""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if isinstance(value, str) and len(value) > 1000:
                    sanitized[key] = value[:1000]
                else:
                    sanitized[key] = value
            return sanitized
        return data
