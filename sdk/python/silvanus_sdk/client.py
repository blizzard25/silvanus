"""
Main Silvanus SDK client implementation.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx

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
    ErrorResponse,
    HealthResponse,
    OAuthCallbackResponse,
    OAuthLoginResponse,
)


class SilvanusClient:
    """
    Silvanus API client supporting both API key and OAuth2.0 authentication.

    This client provides a comprehensive interface to interact with the Silvanus
    Green Energy Rewards API, including activity submission, OAuth2.0 flows,
    and utility endpoints.
    """

    def __init__(
        self,
        base_url: str = "https://silvanus-a4nt.onrender.com",
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        """
        Initialize the Silvanus client.

        Args:
            base_url: Base URL for the Silvanus API
            api_key: API key for authentication (alternative to OAuth)
            access_token: OAuth2.0 access token for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.access_token = access_token
        self.timeout = timeout
        self.max_retries = max_retries

        self._client = httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self) -> "SilvanusClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "silvanus-sdk-python/0.1.0",
        }

        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        elif self.api_key:
            headers["X-API-Key"] = self.api_key

        return headers

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """
        Make HTTP request with error handling and retries.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            retry_count: Current retry attempt

        Returns:
            Response data as dictionary

        Raises:
            Various SilvanusAPIError subclasses based on error type
        """
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        headers = self._get_headers()

        try:
            response = await self._client.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
            )

            if response.headers.get("content-type", "").startswith("application/json"):
                response_data = response.json()
            else:
                response_data = {"status": response.text}

        except httpx.TimeoutException:
            if retry_count < self.max_retries:
                await asyncio.sleep(2**retry_count)  # Exponential backoff
                return await self._make_request(
                    method, endpoint, data, params, retry_count + 1
                )
            raise NetworkError("Request timed out")

        except httpx.RequestError as e:
            if retry_count < self.max_retries:
                await asyncio.sleep(2**retry_count)
                return await self._make_request(
                    method, endpoint, data, params, retry_count + 1
                )
            raise NetworkError(f"Network error: {str(e)}")

        if response.status_code == 401:
            raise AuthenticationError(
                response_data.get("detail", "Authentication failed"),
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code == 403:
            raise AuthenticationError(
                response_data.get("detail", "Access forbidden"),
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code == 422:
            raise ValidationError(
                response_data.get("detail", "Validation error"),
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code == 429:
            raise RateLimitError(
                response_data.get("detail", "Rate limit exceeded"),
                status_code=response.status_code,
                response_data=response_data,
            )
        elif response.status_code >= 400:
            raise SilvanusAPIError(
                response_data.get("detail", f"HTTP {response.status_code} error"),
                status_code=response.status_code,
                response_data=response_data,
            )

        return response_data  # type: ignore

    async def health_check(self) -> HealthResponse:
        """
        Check API health status.

        Returns:
            Health status response
        """
        response_data = await self._make_request("GET", "/healthz")
        return HealthResponse(**response_data)  # type: ignore

    async def get_activity_types(self) -> List[ActivityType]:
        """
        Get supported activity types.

        Returns:
            List of supported activity types
        """
        response_data = await self._make_request("GET", "/activities/types")
        return [ActivityType(**item) for item in response_data]  # type: ignore

    async def submit_activity(
        self, activity: ActivitySubmission, version: str = "v2"
    ) -> ActivityResponse:
        """
        Submit a green energy activity.

        Args:
            activity: Activity submission data
            version: API version to use ("v1", "v2", or "legacy")

        Returns:
            Activity submission response with transaction details
        """
        if version not in ["v1", "v2", "legacy"]:
            raise ValueError("Version must be 'v1', 'v2', or 'legacy'")

        endpoint = (
            f"/{version}/activities/submit"
            if version != "legacy"
            else "/activities/submit"
        )

        response_data = await self._make_request(
            "POST", endpoint, data=activity.model_dump()
        )

        return ActivityResponse(**response_data)  # type: ignore

    async def oauth_login(
        self,
        provider: str,
        redirect_uri: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> OAuthLoginResponse:
        """
        Initiate OAuth2.0 login flow.

        Args:
            provider: OAuth provider name (e.g., "github", "solaredge")
            redirect_uri: Optional custom redirect URI
            user_id: Optional user identifier for session tracking

        Returns:
            OAuth login response with authorization URL and state
        """
        params = {}
        if redirect_uri:
            params["redirect_uri"] = redirect_uri
        if user_id:
            params["user_id"] = user_id

        try:
            response_data = await self._make_request(
                "GET", f"/oauth/login/{provider}", params=params
            )
            return OAuthLoginResponse(**response_data)  # type: ignore
        except SilvanusAPIError as e:
            raise OAuthError(
                f"OAuth login failed: {e.message}", e.status_code, e.response_data
            )

    async def oauth_callback(
        self,
        provider: str,
        code: str,
        state: str,
        wallet_address: str,
        redirect_uri: Optional[str] = None,
        session_key: Optional[str] = None,
    ) -> OAuthCallbackResponse:
        """
        Complete OAuth2.0 callback flow.

        Args:
            provider: OAuth provider name
            code: Authorization code from OAuth provider
            state: State parameter for CSRF protection
            wallet_address: Wallet address to associate with token
            redirect_uri: Optional redirect URI
            session_key: Optional session key for PKCE validation

        Returns:
            OAuth callback response with token information
        """
        params = {"code": code, "state": state, "wallet_address": wallet_address}
        if redirect_uri:
            params["redirect_uri"] = redirect_uri
        if session_key:
            params["session_key"] = session_key

        try:
            response_data = await self._make_request(
                "GET", f"/oauth/callback/{provider}", params=params
            )

            callback_response = OAuthCallbackResponse(**response_data)

            return callback_response
        except SilvanusAPIError as e:
            raise OAuthError(
                f"OAuth callback failed: {e.message}", e.status_code, e.response_data
            )

    def set_access_token(self, access_token: str) -> None:
        """
        Set OAuth2.0 access token for authentication.

        Args:
            access_token: OAuth2.0 access token
        """
        self.access_token = access_token
        self.api_key = None  # Clear API key when using OAuth

    def set_api_key(self, api_key: str) -> None:
        """
        Set API key for authentication.

        Args:
            api_key: API key for authentication
        """
        self.api_key = api_key
        self.access_token = None  # Clear OAuth token when using API key


class SilvanusClientSync:
    """
    Synchronous wrapper for SilvanusClient.

    This provides a synchronous interface to the async SilvanusClient
    for users who prefer synchronous code.
    """

    def __init__(self, **kwargs: Any) -> None:
        self._async_client = SilvanusClient(**kwargs)

    def _run_async(self, coro: Any) -> Any:
        """Run async coroutine in sync context."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(coro)

    def health_check(self) -> HealthResponse:
        return self._run_async(self._async_client.health_check())  # type: ignore

    def get_activity_types(self) -> List[ActivityType]:
        return self._run_async(self._async_client.get_activity_types())  # type: ignore

    def submit_activity(
        self, activity: ActivitySubmission, version: str = "v2"
    ) -> ActivityResponse:
        return self._run_async(self._async_client.submit_activity(activity, version))  # type: ignore

    def oauth_login(
        self,
        provider: str,
        redirect_uri: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> OAuthLoginResponse:
        return self._run_async(  # type: ignore
            self._async_client.oauth_login(provider, redirect_uri, user_id)
        )

    def oauth_callback(
        self,
        provider: str,
        code: str,
        state: str,
        wallet_address: str,
        redirect_uri: Optional[str] = None,
        session_key: Optional[str] = None,
    ) -> OAuthCallbackResponse:
        return self._run_async(  # type: ignore
            self._async_client.oauth_callback(
                provider, code, state, wallet_address, redirect_uri, session_key
            )
        )

    def set_access_token(self, access_token: str) -> None:
        self._async_client.set_access_token(access_token)

    def set_api_key(self, api_key: str) -> None:
        self._async_client.set_api_key(api_key)

    def close(self) -> None:
        self._run_async(self._async_client.close())
