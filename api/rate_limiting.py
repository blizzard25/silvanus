from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from api.auth import get_api_key_tier, APIKeyTier

# Custom key function for tiered rate limiting
def get_tiered_rate_limit_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    if api_key:
        tier = get_api_key_tier(api_key)
        return f"{api_key}:{tier.value}"
    return get_remote_address(request)

def get_rate_limit_for_request(request: Request) -> str:
    api_key = request.headers.get("X-API-Key")
    if api_key:
        tier = get_api_key_tier(api_key)
        if tier == APIKeyTier.ADMIN:
            return "10000/hour"  # Admin: 10k requests/hour
        elif tier == APIKeyTier.PREMIUM:
            return "5000/hour"   # Premium: 5k requests/hour
        else:
            return "1000/hour"   # Basic: 1k requests/hour
    return "100/hour"  # No API key: 100 requests/hour

limiter = Limiter(key_func=get_tiered_rate_limit_key)
