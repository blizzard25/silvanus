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

**Status**: 🚧 Planned  
**Location**: `typescript/`  
**Language**: TypeScript/JavaScript  
**Package Manager**: npm/yarn/pnpm  

The TypeScript SDK will provide web-compatible interface for browser and Node.js applications.

**Planned Features:**
- TypeScript type definitions
- Browser and Node.js compatibility
- OAuth2.0 PKCE flow for web applications
- Promise-based async interface
- Tree-shakeable modules
- CommonJS and ESM support

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

**TypeScript (Planned):**
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

**TypeScript (Planned):**
```typescript
const activity = {
    walletAddress: "0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
    activityType: "solar_export",
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
- **Issues**: Report SDK issues on the main GitHub repository
- **Examples**: Check individual SDK directories for usage examples

## Roadmap

- [x] Python SDK (v0.1.0)
- [ ] TypeScript/JavaScript SDK
- [ ] Go SDK (future consideration)
- [ ] Rust SDK (future consideration)
- [ ] Package publishing to PyPI, npm
- [ ] SDK documentation website
- [ ] Interactive examples and playground

## License

All Silvanus SDKs are part of the Silvanus project and follow the same license terms.
