from fastapi import FastAPI, Request
from api.routes import devices, activities, wallets, activity_types, healthz, oauth_routes
from api.oauth import github 
from api.database import engine, Base
from api.models import tokens

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

# Custom key function for rate limiting (API key or IP)
def get_api_key_or_ip(request: Request):
    return request.headers.get("X-API-Key") or get_remote_address(request)

# Rate limiter (1000 requests per hour)
limiter = Limiter(key_func=get_api_key_or_ip, default_limits=["1000/hour"])

app = FastAPI(title="Silvanus API")

# Register limiter and middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Create tables if they don’t exist
Base.metadata.create_all(bind=engine)

# Register routes
app.include_router(devices.router, prefix="/devices", tags=["Devices"])
app.include_router(activities.router, prefix="/activities", tags=["Activities"])
app.include_router(oauth_routes.router, prefix="/oauth", tags=["OAuth"])
app.include_router(wallets.router, tags=["Wallets"])
app.include_router(activity_types.router, tags=["Activity Types"])
app.include_router(healthz.router)

# For dev db intialization, will be removed for production
@app.on_event("startup")
def init_db():
    from api.models import tokens
    tokens.Base.metadata.create_all(bind=engine)