"""
Silvanus SDK - Python client for the Silvanus Green Energy Rewards API

This SDK provides a comprehensive interface to interact with the Silvanus API,
supporting both API key and OAuth2.0 authentication methods.
"""

from .client import SilvanusClient, SilvanusClientSync
from .exceptions import (
    AuthenticationError,
    NetworkError,
    OAuthError,
    RateLimitError,
    SilvanusAPIError,
    ValidationError,
)
from .models import (
    ActivityResponse,
    ActivitySubmission,
    ActivityType,
    HealthResponse,
    OAuthCallbackResponse,
    OAuthLoginResponse,
)

__version__ = "0.1.0"
__all__ = [
    "SilvanusClient",
    "SilvanusClientSync",
    "ActivitySubmission",
    "ActivityResponse",
    "ActivityType",
    "OAuthLoginResponse",
    "OAuthCallbackResponse",
    "HealthResponse",
    "SilvanusAPIError",
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
    "NetworkError",
    "OAuthError",
]
