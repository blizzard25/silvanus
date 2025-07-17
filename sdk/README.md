# Silvanus SDK

Software Development Kits (SDKs) for the Silvanus Green Energy Rewards API.

## Available SDKs

### Python SDK

**Status**: ✅ Available  
**Location**: `python/`  
**Language**: Python 3.8+  
**Package Manager**: Poetry  

The Python SDK provides a comprehensive async-first interface to the Silvanus API with full support for both API key and OAuth2.0 authentication.

**Key Features:**
- Async/await support with httpx
- Type safety with Pydantic models
- Comprehensive error handling
- OAuth2.0 flow with PKCE validation
- API versioning support (legacy, v1, v2)
- Retry logic with exponential backoff
- Synchronous wrapper for backwards compatibility

**Quick Start:**
```python
from silvanus_sdk import SilvanusClient, ActivitySubmission

async with SilvanusClient(api_key="your-key") as client:
    activity = ActivitySubmission(
        wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
        activity_type="solar_export",
        value=5.0
    )
    response = await client.submit_activity(activity)
    print(f"Transaction: {response.txHash}")
```

### TypeScript/JavaScript SDK

**Status**: ✅ Available  
**Location**: `typescript/`  
**Language**: TypeScript/JavaScript  
**Package Manager**: npm/yarn/pnpm  

The TypeScript SDK provides a modern, type-safe interface for browser and Node.js applications with comprehensive API coverage and dual authentication support.

**Key Features:**
- TypeScript type definitions with Zod runtime validation
- Browser and Node.js compatibility (ESM & CommonJS)
- OAuth2.0 PKCE flow for web applications
- Promise-based async interface with axios HTTP client
- Tree-shakeable modules with modern build system
- Comprehensive error handling with custom exception hierarchy
- Retry logic with exponential backoff
- API versioning support (legacy, v1, v2)

**Quick Start:**
```typescript
import { SilvanusClient, ActivitySubmission } from '@silvanus/sdk';

const client = new SilvanusClient({ apiKey: 'your-key' });

const activity: ActivitySubmission = {
  wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
  activity_type: 'solar_export',
  value: 5.0
};

const response = await client.submitActivity(activity);
console.log(`Transaction: ${response.txHash}`);
```

## SDK Architecture

All Silvanus SDKs follow a consistent architecture:

### Core Components

1. **Client Class**: Main interface for API interactions
2. **Models**: Type-safe data structures matching API schemas
3. **Authentication**: Support for API keys and OAuth2.0 tokens
4. **Error Handling**: Custom exceptions for different error scenarios
5. **Validation**: Input validation matching API requirements

### Supported Endpoints

All SDKs wrap these core Silvanus API endpoints:

| Endpoint | Purpose | Versions |
|----------|---------|----------|
| `/healthz` | API health check | All |
| `/activities/types` | Get supported activity types | All |
| `/activities/submit` | Submit green energy activity | Legacy, V1, V2 |
| `/oauth/login/{provider}` | Initiate OAuth2.0 flow | All |
| `/oauth/callback/{provider}` | Complete OAuth2.0 flow | All |

### Authentication Methods

1. **API Key Authentication**
   - Header: `X-API-Key: your-api-key`
   - Simple and direct
   - Suitable for server-side applications

2. **OAuth2.0 Bearer Token**
   - Header: `Authorization: Bearer your-token`
   - Provider-agnostic (GitHub, SolarEdge, custom)
   - PKCE validation for security
   - Suitable for user-facing applications

### Provider-Agnostic OAuth2.0

The Silvanus API supports multiple OAuth providers through a unified interface:

| Provider | Status | Use Case |
|----------|--------|----------|
| GitHub | Active | Internal testing and development |
| SolarEdge | Available | Production solar data integration |
| Custom | Extensible | Add your own OAuth provider |

## Development Guidelines

### SDK Standards

All Silvanus SDKs should follow these standards:

1. **Consistent API**: Similar method names and patterns across languages
2. **Type Safety**: Strong typing where supported by the language
3. **Error Handling**: Comprehensive error handling with custom exceptions
4. **Documentation**: Inline documentation and usage examples
5. **Testing**: Unit tests, integration tests, and example validation
6. **Async Support**: Native async patterns for the target language

### Testing Strategy

Each SDK includes:

1. **Unit Tests**: Test individual components and methods
2. **Integration Tests**: Test against live API endpoints
3. **Mock Tests**: Test error scenarios and edge cases
4. **Example Validation**: Ensure all examples work correctly

### CI/CD Pipeline

- Automated testing on pull requests
- Code quality checks (linting, formatting, type checking)
- Example validation
- Documentation generation
- Package publishing (when ready)

## Usage Examples

### Health Check

**Python:**
```python
health = await client.health_check()
print(f"Status: {health.status}")
```

**TypeScript:**
```typescript
const health = await client.healthCheck();
console.log(`Status: ${health.status}`);
```

### Activity Submission

**Python:**
```python
activity = ActivitySubmission(
    wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
    activity_type="solar_export",
    value=5.0
)
response = await client.submit_activity(activity, version="v2")
```

**TypeScript:**
```typescript
const activity: ActivitySubmission = {
    wallet_address: "0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
    activity_type: "solar_export",
    value: 5.0
};
const response = await client.submitActivity(activity, "v2");
```

### OAuth2.0 Flow

**Python:**
```python
# Initiate OAuth
login_response = await client.oauth_login(provider="github")
# Complete callback
callback_response = await client.oauth_callback(
    provider="github",
    code="auth-code",
    state=login_response.state,
    wallet_address="0x...",
    session_key=login_response.session_key
)
```

**TypeScript:**
```typescript
// Initiate OAuth
const loginResponse = await client.oauthLogin('github');
// Complete callback
const callbackParams: OAuthCallbackParams = {
    provider: 'github',
    code: 'auth-code',
    state: loginResponse.state,
    wallet_address: '0x...',
    session_key: loginResponse.session_key
};
const callbackResponse = await client.oauthCallback(callbackParams);
```

## SDK Feature Comparison

| Feature | Python SDK | TypeScript SDK |
|---------|------------|----------------|
| **Authentication** | API Key + OAuth2.0 | API Key + OAuth2.0 |
| **OAuth Providers** | GitHub, SolarEdge, Custom | GitHub, SolarEdge, Custom |
| **API Versions** | Legacy, V1, V2 | Legacy, V1, V2 |
| **Type Safety** | Pydantic models | Zod schemas + TypeScript |
| **Async Support** | Native async/await | Promise-based |
| **Sync Support** | Wrapper class | N/A (Promise-based) |
| **Error Handling** | Custom exceptions | Custom exception classes |
| **Retry Logic** | Exponential backoff | Exponential backoff |
| **HTTP Client** | httpx | axios |
| **Build System** | Poetry | Vite |
| **Testing** | pytest | Vitest |
| **Runtime** | Python 3.8+ | Node.js 16+ / Browser |

## Advanced Usage Examples

### Error Handling Comparison

**Python:**
```python
from silvanus_sdk import (
    AuthenticationError, ValidationError, 
    RateLimitError, NetworkError, OAuthError
)

try:
    response = await client.submit_activity(activity)
except AuthenticationError as e:
    print(f"Auth failed: {e.message} (Status: {e.status_code})")
except ValidationError as e:
    print(f"Validation error: {e.message}")
except RateLimitError as e:
    print(f"Rate limited: {e.message}")
```

**TypeScript:**
```typescript
import {
  AuthenticationError, ValidationError,
  RateLimitError, NetworkError, OAuthError
} from '@silvanus/sdk';

try {
  const response = await client.submitActivity(activity);
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.log(`Auth failed: ${error.message} (Status: ${error.statusCode})`);
  } else if (error instanceof ValidationError) {
    console.log(`Validation error: ${error.message}`);
  } else if (error instanceof RateLimitError) {
    console.log(`Rate limited: ${error.message}`);
  }
}
```

### Batch Operations

**Python:**
```python
import asyncio

async def batch_submit():
    async with SilvanusClient(api_key="your-key") as client:
        activities = [
            ActivitySubmission(wallet_address="0x...", activity_type="solar_export", value=5.0),
            ActivitySubmission(wallet_address="0x...", activity_type="ev_charging", value=3.0),
        ]
        
        tasks = [client.submit_activity(activity) for activity in activities]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            print(f"Transaction: {result.txHash}")
```

**TypeScript:**
```typescript
async function batchSubmit() {
  const client = new SilvanusClient({ apiKey: 'your-key' });
  
  const activities: ActivitySubmission[] = [
    { wallet_address: '0x...', activity_type: 'solar_export', value: 5.0 },
    { wallet_address: '0x...', activity_type: 'ev_charging', value: 3.0 },
  ];
  
  const promises = activities.map(activity => client.submitActivity(activity));
  const results = await Promise.all(promises);
  
  results.forEach(result => {
    console.log(`Transaction: ${result.txHash}`);
  });
}
```

### OAuth2.0 Complete Flow

**Python:**
```python
async def complete_oauth_flow():
    client = SilvanusClient()
    
    # Step 1: Initiate OAuth login
    login_response = await client.oauth_login(
        provider="github",
        redirect_uri="https://your-app.com/callback"
    )
    
    print(f"Visit: {login_response.auth_url}")
    print(f"State: {login_response.state}")
    
    # Step 2: Handle callback (after user authorization)
    callback_response = await client.oauth_callback(
        provider="github",
        code="authorization-code-from-callback",
        state=login_response.state,
        wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
        session_key=login_response.session_key
    )
    
    # Step 3: Use OAuth token
    client.set_access_token(callback_response.access_token)
    
    # Now make authenticated requests
    health = await client.health_check()
    print(f"Authenticated as: {health.status}")
```

**TypeScript:**
```typescript
async function completeOAuthFlow() {
  const client = new SilvanusClient();
  
  // Step 1: Initiate OAuth login
  const loginResponse = await client.oauthLogin(
    'github',
    'https://your-app.com/callback'
  );
  
  console.log(`Visit: ${loginResponse.auth_url}`);
  console.log(`State: ${loginResponse.state}`);
  
  // Step 2: Handle callback (after user authorization)
  const callbackParams: OAuthCallbackParams = {
    provider: 'github',
    code: 'authorization-code-from-callback',
    state: loginResponse.state,
    wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
    session_key: loginResponse.session_key
  };
  
  const callbackResponse = await client.oauthCallback(callbackParams);
  
  // Step 3: Use OAuth token
  client.setAccessToken(callbackResponse.access_token);
  
  // Now make authenticated requests
  const health = await client.healthCheck();
  console.log(`Authenticated as: ${health.status}`);
}
```

## Contributing

### Adding a New SDK

1. Create directory: `sdk/{language}/`
2. Follow the SDK architecture guidelines
3. Implement core components (client, models, auth, errors)
4. Add comprehensive tests
5. Create usage examples
6. Update this README

### SDK Development Workflow

1. **Investigation**: Study API endpoints and authentication
2. **Design**: Plan SDK architecture and public interface
3. **Implementation**: Build core functionality
4. **Testing**: Add unit and integration tests
5. **Documentation**: Create README and examples
6. **Validation**: Test against live API
7. **Review**: Code review and feedback
8. **Release**: Package and publish

## Support

- **API Documentation**: See `api/README.md` for detailed API documentation
- **Python SDK**: See `python/README.md` for Python-specific documentation
- **TypeScript SDK**: See `typescript/README.md` for TypeScript-specific documentation
- **Issues**: Report SDK issues on the main GitHub repository
- **Examples**: Check individual SDK directories for usage examples

## Roadmap

- [x] Python SDK (v0.1.0) - Complete with async/sync support, OAuth2.0, comprehensive testing
- [x] TypeScript/JavaScript SDK (v0.1.0) - Complete with type safety, dual auth, modern tooling
- [ ] Package publishing to PyPI, npm
- [ ] SDK documentation website
- [ ] Interactive examples and playground
- [ ] Go SDK (future consideration)
- [ ] Rust SDK (future consideration)

## License

All Silvanus SDKs are part of the Silvanus project and follow the same license terms.
