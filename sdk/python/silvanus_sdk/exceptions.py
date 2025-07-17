"""
Custom exceptions for the Silvanus SDK.
"""

from typing import Any, Dict, Optional


class SilvanusAPIError(Exception):
    """Base exception for all Silvanus API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


class AuthenticationError(SilvanusAPIError):
    """Raised when authentication fails."""

    pass


class ValidationError(SilvanusAPIError):
    """Raised when request validation fails."""

    pass


class RateLimitError(SilvanusAPIError):
    """Raised when rate limit is exceeded."""

    pass


class NetworkError(SilvanusAPIError):
    """Raised when network/connection issues occur."""

    pass


class OAuthError(SilvanusAPIError):
    """Raised when OAuth flow encounters errors."""

    pass
