# Silvanus Python SDK

A comprehensive Python SDK for the Silvanus Green Energy Rewards API, supporting both API key and OAuth2.0 authentication methods.

## Features

- **Dual Authentication**: Support for both API key and OAuth2.0 bearer token authentication
- **Provider-Agnostic OAuth**: Works with GitHub, SolarEdge, and custom OAuth providers
- **Async-First Design**: Built with modern async/await patterns using httpx
- **Type Safety**: Full Pydantic model validation and type hints
- **Comprehensive Error Handling**: Custom exceptions for different error scenarios
- **Retry Logic**: Automatic retry with exponential backoff for network issues
- **API Versioning**: Support for legacy, v1, and v2 API endpoints
- **Synchronous Wrapper**: Optional sync interface for backwards compatibility

## Installation

### Using Poetry (Recommended)

```bash
cd sdk/python
poetry install
```

### Using pip

```bash
cd sdk/python
pip install -e .
```

## Quick Start

### API Key Authentication

```python
import asyncio
from silvanus_sdk import SilvanusClient, ActivitySubmission

async def main():
    async with SilvanusClient(api_key="your-api-key") as client:
        # Check API health
        health = await client.health_check()
        print(f"API Status: {health.status}")
        
        # Submit green energy activity
        activity = ActivitySubmission(
            wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
            activity_type="solar_export",
            value=5.0,
            details={"panel_count": 10}
        )
        
        response = await client.submit_activity(activity)
        print(f"Transaction: {response.txHash}")

asyncio.run(main())
```

### OAuth2.0 Authentication

```python
import asyncio
from silvanus_sdk import SilvanusClient

async def oauth_flow():
    client = SilvanusClient()
    
    # Step 1: Initiate OAuth login
    login_response = await client.oauth_login(provider="github")
    print(f"Visit: {login_response.auth_url}")
    
    # Step 2: After user authorization, complete callback
    # (You would get 'code' from the OAuth callback URL)
    callback_response = await client.oauth_callback(
        provider="github",
        code="authorization-code-from-callback",
        state=login_response.state,
        wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
        session_key=login_response.session_key
    )
    
    # Step 3: Use OAuth token for API calls
    client.set_access_token("oauth-access-token-from-response")
    
    health = await client.health_check()
    print(f"Authenticated Status: {health.status}")
    
    await client.close()

asyncio.run(oauth_flow())
```

### Synchronous Usage

```python
from silvanus_sdk import SilvanusClientSync, ActivitySubmission

# Synchronous client for users who prefer sync code
client = SilvanusClientSync(api_key="your-api-key")

try:
    health = client.health_check()
    print(f"API Status: {health.status}")
    
    activity = ActivitySubmission(
        wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
        activity_type="solar_export",
        value=3.5
    )
    
    response = client.submit_activity(activity)
    print(f"Transaction: {response.txHash}")
    
finally:
    client.close()
```

## API Reference

### SilvanusClient

The main async client class for interacting with the Silvanus API.

#### Constructor

```python
SilvanusClient(
    base_url: str = "https://silvanus-a4nt.onrender.com",
    api_key: Optional[str] = None,
    access_token: Optional[str] = None,
    timeout: float = 30.0,
    max_retries: int = 3,
)
```

#### Methods

##### Health and Utility

- `health_check() -> HealthResponse`: Check API health status
- `get_activity_types() -> List[ActivityType]`: Get supported activity types

##### Activity Submission

- `submit_activity(activity: ActivitySubmission, version: str = "v2") -> ActivityResponse`: Submit green energy activity

##### OAuth2.0 Flow

- `oauth_login(provider: str, redirect_uri: Optional[str] = None, user_id: Optional[str] = None) -> OAuthLoginResponse`: Initiate OAuth login
- `oauth_callback(provider: str, code: str, state: str, wallet_address: str, ...) -> OAuthCallbackResponse`: Complete OAuth callback

##### Authentication Management

- `set_access_token(access_token: str)`: Set OAuth2.0 access token
- `set_api_key(api_key: str)`: Set API key for authentication

### Models

#### ActivitySubmission

```python
ActivitySubmission(
    wallet_address: str,        # Ethereum wallet address (validated)
    activity_type: str,         # Type of green activity
    value: float,              # Activity value in kWh (0-10000)
    details: Dict[str, Any] = {}  # Additional activity details
)
```

**Supported Activity Types:**
- `solar_export`: Solar energy exported to grid
- `ev_charging`: Electric vehicle charging
- `energy_saving`: Energy conservation activities
- `carbon_offset`: Carbon offset purchases
- `renewable_energy`: Renewable energy usage
- `green_transport`: Green transportation
- `waste_reduction`: Waste reduction activities

#### ActivityResponse

```python
ActivityResponse(
    txHash: str,    # Blockchain transaction hash
    status: str     # Transaction status (confirmed/pending)
)
```

### Error Handling

The SDK provides comprehensive error handling with custom exceptions:

```python
from silvanus_sdk import (
    SilvanusAPIError,      # Base exception
    AuthenticationError,   # 401/403 errors
    ValidationError,       # 422 validation errors
    RateLimitError,       # 429 rate limit errors
    NetworkError,         # Network/timeout errors
    OAuthError           # OAuth flow errors
)

try:
    response = await client.submit_activity(activity)
except AuthenticationError as e:
    print(f"Auth failed: {e.message} (Status: {e.status_code})")
except ValidationError as e:
    print(f"Validation error: {e.message}")
except RateLimitError as e:
    print(f"Rate limited: {e.message}")
except NetworkError as e:
    print(f"Network error: {e.message}")
```

## API Versions

The SDK supports all API versions:

- **v2** (recommended): Latest version with enhanced validation and security
- **v1**: Stable version with basic validation
- **legacy**: Original endpoint for backwards compatibility

```python
# Use different API versions
response_v2 = await client.submit_activity(activity, version="v2")
response_v1 = await client.submit_activity(activity, version="v1")
response_legacy = await client.submit_activity(activity, version="legacy")
```

## OAuth2.0 Providers

The SDK supports multiple OAuth providers:

| Provider | Status | Use Case |
|----------|--------|----------|
| GitHub | Active | Internal testing and development |
| SolarEdge | Available | Production solar data integration |
| Custom | Extensible | Add your own OAuth provider |

### Provider-Specific Examples

```python
# GitHub OAuth (for testing)
github_login = await client.oauth_login(provider="github")

# SolarEdge OAuth (for production)
solaredge_login = await client.oauth_login(provider="solaredge")
```

## Advanced Usage

### Batch Operations

```python
import asyncio

async def batch_submit():
    async with SilvanusClient(api_key="your-key") as client:
        activities = [
            ActivitySubmission(wallet_address="0x...", activity_type="solar_export", value=5.0),
            ActivitySubmission(wallet_address="0x...", activity_type="ev_charging", value=3.0),
            ActivitySubmission(wallet_address="0x...", activity_type="energy_saving", value=2.0),
        ]
        
        # Submit all activities concurrently
        tasks = [client.submit_activity(activity) for activity in activities]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            print(f"Transaction: {result.txHash}")
```

### Custom Configuration

```python
# Configure timeout and retry behavior
client = SilvanusClient(
    api_key="your-key",
    timeout=60.0,      # 60 second timeout
    max_retries=5      # 5 retry attempts
)
```

### Context Manager

```python
# Automatic cleanup with context manager
async with SilvanusClient(api_key="your-key") as client:
    health = await client.health_check()
    # Client automatically closed when exiting context
```

## Development

### Running Tests

```bash
cd sdk/python
poetry run pytest tests/ -v
```

### Code Quality

```bash
# Format code
poetry run black silvanus_sdk/

# Sort imports
poetry run isort silvanus_sdk/

# Type checking
poetry run mypy silvanus_sdk/
```

### Examples

See the `examples/` directory for comprehensive usage examples:

- `basic_usage.py`: API key authentication and basic operations
- `oauth_flow.py`: OAuth2.0 authentication flow
- `async_usage.py`: Advanced async patterns and error handling

## Migration Guide

### From Direct API Usage

If you're currently using the API directly, here's how to migrate:

**Before (Direct API):**
```python
import requests

response = requests.post(
    "https://silvanus-a4nt.onrender.com/v2/activities/submit",
    headers={"X-API-Key": "your-key"},
    json={
        "wallet_address": "0x...",
        "activity_type": "solar_export",
        "value": 5.0
    }
)
```

**After (SDK):**
```python
from silvanus_sdk import SilvanusClient, ActivitySubmission

async with SilvanusClient(api_key="your-key") as client:
    activity = ActivitySubmission(
        wallet_address="0x...",
        activity_type="solar_export",
        value=5.0
    )
    response = await client.submit_activity(activity)
```

## Support

- **API Documentation**: See the main API README for detailed endpoint documentation
- **Issues**: Report issues on the GitHub repository
- **Examples**: Check the `examples/` directory for usage patterns

## License

This SDK is part of the Silvanus project and follows the same license terms.
