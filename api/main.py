from fastapi import FastAPI, Request
from api.routes import devices, activities, wallets, activity_types, healthz, oauth_routes
from api.routes.v1 import activities as v1_activities
from api.routes.v2 import activities as v2_activities
from api.oauth import github 
from api.database import engine, Base
from api.models import tokens
from api.rate_limiting import limiter
from api.security_middleware import SecurityMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

app = FastAPI(title="Silvanus API")

app.add_middleware(SecurityMiddleware, max_request_size=1024 * 1024)

# Register limiter and middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Create tables if they don’t exist
Base.metadata.create_all(bind=engine)

# Register versioned routes
app.include_router(v1_activities.router, prefix="/v1/activities", tags=["V1 Activities"])
app.include_router(v2_activities.router, prefix="/v2/activities", tags=["V2 Activities"])

# Register unversioned routes (backward compatibility - defaults to V1 behavior)
app.include_router(activities.router, prefix="/activities", tags=["Activities (Legacy)"])
app.include_router(devices.router, prefix="/devices", tags=["Devices"])
app.include_router(oauth_routes.router, prefix="/oauth", tags=["OAuth"])
app.include_router(wallets.router, tags=["Wallets"])
app.include_router(activity_types.router, tags=["Activity Types"])
app.include_router(healthz.router)

# For dev db intialization, will be removed for production
@app.on_event("startup")
def init_db():
    from api.models import tokens
    tokens.Base.metadata.create_all(bind=engine)
