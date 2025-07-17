"""
Comprehensive test suite for the Silvanus SDK client.
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from silvanus_sdk import (
    SilvanusClient,
    SilvanusClientSync,
    ActivitySubmission,
    ActivityResponse,
    ActivityType,
    OAuthLoginResponse,
    OAuthCallbackResponse,
    HealthResponse,
    SilvanusAPIError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NetworkError,
    OAuthError,
)


class TestSilvanusClient:
    """Test suite for async SilvanusClient."""
    
    @pytest.fixture
    def client(self):
        """Create test client instance."""
        return SilvanusClient(
            base_url="https://test-api.silvanus.com",
            api_key="test-api-key"
        )
        
    @pytest.fixture
    def oauth_client(self):
        """Create test client with OAuth token."""
        return SilvanusClient(
            base_url="https://test-api.silvanus.com",
            access_token="test-oauth-token"
        )
        
    @pytest.mark.asyncio
    async def test_health_check_success(self, client):
        """Test successful health check."""
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"status": "ok"}
            
            result = await client.health_check()
            
            assert isinstance(result, HealthResponse)
            assert result.status == "ok"
            mock_request.assert_called_once_with("GET", "/healthz")
            
    @pytest.mark.asyncio
    async def test_get_activity_types_success(self, client):
        """Test successful activity types retrieval."""
        mock_response = [
            {
                "type": "solar_export",
                "description": "Solar energy exported to grid",
                "expectedDetails": ["panel_count", "efficiency"]
            }
        ]
        
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.get_activity_types()
            
            assert len(result) == 1
            assert isinstance(result[0], ActivityType)
            assert result[0].type == "solar_export"
            mock_request.assert_called_once_with("GET", "/activities/types")
            
    @pytest.mark.asyncio
    async def test_submit_activity_v2_success(self, client):
        """Test successful activity submission to v2 endpoint."""
        activity = ActivitySubmission(
            wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
            activity_type="solar_export",
            value=5.0,
            details={"panel_count": 10}
        )
        
        mock_response = {
            "txHash": "0x123abc...",
            "status": "confirmed"
        }
        
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.submit_activity(activity, version="v2")
            
            assert isinstance(result, ActivityResponse)
            assert result.txHash == "0x123abc..."
            assert result.status == "confirmed"
            mock_request.assert_called_once_with(
                "POST",
                "/v2/activities/submit",
                data=activity.model_dump()
            )
            
    @pytest.mark.asyncio
    async def test_submit_activity_legacy_success(self, client):
        """Test successful activity submission to legacy endpoint."""
        activity = ActivitySubmission(
            wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
            activity_type="solar_export",
            value=5.0
        )
        
        mock_response = {
            "txHash": "0x456def...",
            "status": "pending"
        }
        
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.submit_activity(activity, version="legacy")
            
            assert isinstance(result, ActivityResponse)
            assert result.txHash == "0x456def..."
            mock_request.assert_called_once_with(
                "POST",
                "/activities/submit",
                data=activity.model_dump()
            )
            
    @pytest.mark.asyncio
    async def test_oauth_login_success(self, client):
        """Test successful OAuth login initiation."""
        mock_response = {
            "auth_url": "https://github.com/login/oauth/authorize?...",
            "state": "random-state-123",
            "session_key": "session-key-456",
            "provider": "github"
        }
        
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.oauth_login("github", user_id="test-user")
            
            assert isinstance(result, OAuthLoginResponse)
            assert result.provider == "github"
            assert "github.com" in result.auth_url
            mock_request.assert_called_once_with(
                "GET",
                "/oauth/login/github",
                params={"user_id": "test-user"}
            )
            
    @pytest.mark.asyncio
    async def test_oauth_callback_success(self, client):
        """Test successful OAuth callback processing."""
        mock_response = {
            "message": "OAuth token stored successfully",
            "provider": "github",
            "wallet_address": "0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
            "token_id": 123,
            "expires_in": 3600,
            "expires_at": "2024-01-01T12:00:00Z",
            "has_refresh_token": False
        }
        
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.oauth_callback(
                provider="github",
                code="auth-code-123",
                state="state-456",
                wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2"
            )
            
            assert isinstance(result, OAuthCallbackResponse)
            assert result.provider == "github"
            assert result.token_id == 123
            
    @pytest.mark.asyncio
    async def test_authentication_headers_api_key(self, client):
        """Test API key authentication headers."""
        headers = client._get_headers()
        
        assert headers["X-API-Key"] == "test-api-key"
        assert "Authorization" not in headers
        
    @pytest.mark.asyncio
    async def test_authentication_headers_oauth(self, oauth_client):
        """Test OAuth authentication headers."""
        headers = oauth_client._get_headers()
        
        assert headers["Authorization"] == "Bearer test-oauth-token"
        assert "X-API-Key" not in headers
        
    @pytest.mark.asyncio
    async def test_error_handling_401(self, client):
        """Test 401 authentication error handling."""
        with patch.object(client._client, 'request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"detail": "Invalid API key"}
            mock_response.headers = {"content-type": "application/json"}
            mock_request.return_value = mock_response
            
            with pytest.raises(AuthenticationError) as exc_info:
                await client._make_request("GET", "/test")
                
            assert exc_info.value.status_code == 401
            assert "Invalid API key" in str(exc_info.value)
            
    @pytest.mark.asyncio
    async def test_error_handling_422(self, client):
        """Test 422 validation error handling."""
        with patch.object(client._client, 'request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 422
            mock_response.json.return_value = {"detail": "Validation failed"}
            mock_response.headers = {"content-type": "application/json"}
            mock_request.return_value = mock_response
            
            with pytest.raises(ValidationError) as exc_info:
                await client._make_request("POST", "/test")
                
            assert exc_info.value.status_code == 422
            
    @pytest.mark.asyncio
    async def test_error_handling_429(self, client):
        """Test 429 rate limit error handling."""
        with patch.object(client._client, 'request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.json.return_value = {"detail": "Rate limit exceeded"}
            mock_response.headers = {"content-type": "application/json"}
            mock_request.return_value = mock_response
            
            with pytest.raises(RateLimitError) as exc_info:
                await client._make_request("POST", "/test")
                
            assert exc_info.value.status_code == 429
            
    @pytest.mark.asyncio
    async def test_retry_logic_timeout(self, client):
        """Test retry logic for timeout errors."""
        client.max_retries = 2
        
        with patch.object(client._client, 'request') as mock_request:
            mock_request.side_effect = httpx.TimeoutException("Request timeout")
            
            with pytest.raises(NetworkError) as exc_info:
                await client._make_request("GET", "/test")
                
            assert "Request timed out" in str(exc_info.value)
            assert mock_request.call_count == 3  # Initial + 2 retries
            
    @pytest.mark.asyncio
    async def test_set_access_token(self, client):
        """Test setting OAuth access token."""
        client.set_access_token("new-oauth-token")
        
        assert client.access_token == "new-oauth-token"
        assert client.api_key is None
        
    @pytest.mark.asyncio
    async def test_set_api_key(self, oauth_client):
        """Test setting API key."""
        oauth_client.set_api_key("new-api-key")
        
        assert oauth_client.api_key == "new-api-key"
        assert oauth_client.access_token is None


class TestSilvanusClientSync:
    """Test suite for synchronous SilvanusClientSync."""
    
    @pytest.fixture
    def sync_client(self):
        """Create synchronous test client."""
        return SilvanusClientSync(
            base_url="https://test-api.silvanus.com",
            api_key="test-api-key"
        )
        
    def test_health_check_sync(self, sync_client):
        """Test synchronous health check."""
        with patch.object(sync_client._async_client, 'health_check', new_callable=AsyncMock) as mock_health:
            mock_health.return_value = HealthResponse(status="ok")
            
            result = sync_client.health_check()
            
            assert isinstance(result, HealthResponse)
            assert result.status == "ok"
            
    def test_submit_activity_sync(self, sync_client):
        """Test synchronous activity submission."""
        activity = ActivitySubmission(
            wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
            activity_type="solar_export",
            value=5.0
        )
        
        expected_response = ActivityResponse(
            txHash="0x123abc...",
            status="confirmed"
        )
        
        with patch.object(sync_client._async_client, 'submit_activity', new_callable=AsyncMock) as mock_submit:
            mock_submit.return_value = expected_response
            
            result = sync_client.submit_activity(activity)
            
            assert isinstance(result, ActivityResponse)
            assert result.txHash == "0x123abc..."


class TestActivitySubmissionValidation:
    """Test suite for ActivitySubmission model validation."""
    
    def test_valid_activity_submission(self):
        """Test valid activity submission creation."""
        activity = ActivitySubmission(
            wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
            activity_type="solar_export",
            value=5.0,
            details={"panel_count": 10}
        )
        
        assert activity.wallet_address == "0x742D35CC6634c0532925A3b8d4C2C2c2C2c2c2C2"
        assert activity.activity_type == "solar_export"
        assert activity.value == 5.0
        
    def test_invalid_wallet_address(self):
        """Test invalid wallet address validation."""
        with pytest.raises(ValueError) as exc_info:
            ActivitySubmission(
                wallet_address="invalid-address",
                activity_type="solar_export",
                value=5.0
            )
            
        assert "Invalid Ethereum wallet address format" in str(exc_info.value)
        
    def test_invalid_activity_type(self):
        """Test invalid activity type validation."""
        with pytest.raises(ValueError) as exc_info:
            ActivitySubmission(
                wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
                activity_type="invalid_type",
                value=5.0
            )
            
        assert "Invalid activity type" in str(exc_info.value)
        
    def test_invalid_value_negative(self):
        """Test negative value validation."""
        with pytest.raises(ValueError) as exc_info:
            ActivitySubmission(
                wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
                activity_type="solar_export",
                value=-1.0
            )
            
        assert "greater than or equal to 0" in str(exc_info.value)
        
    def test_invalid_value_too_large(self):
        """Test value too large validation."""
        with pytest.raises(ValueError) as exc_info:
            ActivitySubmission(
                wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
                activity_type="solar_export",
                value=15000.0
            )
            
        assert "less than or equal to 10000" in str(exc_info.value)
