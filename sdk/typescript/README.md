# Silvanus TypeScript/JavaScript SDK

A comprehensive TypeScript/JavaScript SDK for the Silvanus Green Energy Rewards API, supporting both API key and OAuth2.0 authentication methods.

## Features

- **Dual Authentication**: Support for both API key and OAuth2.0 bearer token authentication
- **Provider-Agnostic OAuth**: Works with GitHub, SolarEdge, and custom OAuth providers
- **Type Safety**: Full TypeScript support with Zod runtime validation
- **Modern HTTP Client**: Built with axios for reliable HTTP requests
- **Comprehensive Error Handling**: Custom exception hierarchy for different error scenarios
- **Retry Logic**: Automatic retry with exponential backoff for network issues
- **API Versioning**: Support for legacy, v1, and v2 API endpoints
- **ESM & CommonJS**: Dual build support for maximum compatibility

## Installation

### Using npm

```bash
cd sdk/typescript
npm install
```

### Using yarn

```bash
cd sdk/typescript
yarn install
```

### Using pnpm

```bash
cd sdk/typescript
pnpm install
```

## Quick Start

### API Key Authentication

```typescript
import { SilvanusClient, ActivitySubmission } from '@silvanus/sdk';

async function main() {
  const client = new SilvanusClient({
    apiKey: 'your-api-key',
    baseUrl: 'https://silvanus-a4nt.onrender.com'
  });

  try {
    // Check API health
    const health = await client.healthCheck();
    console.log(`API Status: ${health.status}`);

    // Submit green energy activity
    const activity: ActivitySubmission = {
      wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
      activity_type: 'solar_export',
      value: 5.0,
      details: { panel_count: 10 }
    };

    const response = await client.submitActivity(activity);
    console.log(`Transaction: ${response.txHash}`);

  } catch (error) {
    console.error('Error:', error);
  }
}

main();
```

### OAuth2.0 Authentication

```typescript
import { SilvanusClient, OAuthCallbackParams } from '@silvanus/sdk';

async function oauthFlow() {
  const client = new SilvanusClient({
    baseUrl: 'https://silvanus-a4nt.onrender.com'
  });

  try {
    // Step 1: Initiate OAuth login
    const loginResponse = await client.oauthLogin('github');
    console.log(`Visit: ${loginResponse.auth_url}`);

    // Step 2: After user authorization, complete callback
    const callbackParams: OAuthCallbackParams = {
      provider: 'github',
      code: 'authorization-code-from-callback',
      state: loginResponse.state,
      wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
      session_key: loginResponse.session_key
    };

    const callbackResponse = await client.oauthCallback(callbackParams);
    
    // Step 3: Use OAuth token for API calls
    client.setAccessToken('oauth-access-token-from-response');
    
    const health = await client.healthCheck();
    console.log(`Authenticated Status: ${health.status}`);

  } catch (error) {
    console.error('OAuth error:', error);
  }
}

oauthFlow();
```

## API Reference

### SilvanusClient

The main client class for interacting with the Silvanus API.

#### Constructor

```typescript
new SilvanusClient(config?: SilvanusClientConfig)
```

**SilvanusClientConfig:**
```typescript
interface SilvanusClientConfig {
  baseUrl?: string;           // Default: 'https://silvanus-a4nt.onrender.com'
  apiKey?: string;            // API key for authentication
  accessToken?: string;       // OAuth2.0 access token
  timeout?: number;           // Request timeout in ms (default: 30000)
  maxRetries?: number;        // Max retry attempts (default: 3)
}
```

#### Methods

##### Health and Utility

- `healthCheck(): Promise<HealthResponse>` - Check API health status
- `getActivityTypes(): Promise<ActivityTypeInfo[]>` - Get supported activity types

##### Activity Submission

- `submitActivity(activity: ActivitySubmission, version?: 'legacy' | 'v1' | 'v2'): Promise<ActivityResponse>` - Submit green energy activity

##### OAuth2.0 Flow

- `oauthLogin(provider: string, redirectUri?: string, userId?: string): Promise<OAuthLoginResponse>` - Initiate OAuth login
- `oauthCallback(params: OAuthCallbackParams): Promise<OAuthCallbackResponse>` - Complete OAuth callback

##### Authentication Management

- `setAccessToken(accessToken: string): void` - Set OAuth2.0 access token
- `setApiKey(apiKey: string): void` - Set API key for authentication

### Types and Interfaces

#### ActivitySubmission

```typescript
interface ActivitySubmission {
  wallet_address: string;        // Ethereum wallet address (validated)
  activity_type: ActivityType;   // Type of green activity
  value: number;                // Activity value in kWh (0-10000)
  details?: Record<string, any>; // Additional activity details
}
```

**Supported Activity Types:**
- `solar_export` - Solar energy exported to grid
- `ev_charging` - Electric vehicle charging
- `energy_saving` - Energy conservation activities
- `carbon_offset` - Carbon offset purchases
- `renewable_energy` - Renewable energy usage
- `green_transport` - Green transportation
- `waste_reduction` - Waste reduction activities

#### ActivityResponse

```typescript
interface ActivityResponse {
  txHash: string;    // Blockchain transaction hash
  status: string;    // Transaction status (confirmed/pending)
}
```

#### OAuthCallbackParams

```typescript
interface OAuthCallbackParams {
  provider: string;
  code: string;
  state: string;
  wallet_address: string;
  session_key: string;
  code_verifier?: string;
}
```

### Error Handling

The SDK provides comprehensive error handling with custom exceptions:

```typescript
import {
  SilvanusAPIError,      // Base exception
  AuthenticationError,   // 401/403 errors
  ValidationError,       // 422 validation errors
  RateLimitError,       // 429 rate limit errors
  NetworkError,         // Network/timeout errors
  OAuthError           // OAuth flow errors
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
  } else if (error instanceof NetworkError) {
    console.log(`Network error: ${error.message}`);
  }
}
```

## API Versions

The SDK supports all API versions:

- **v2** (recommended): Latest version with enhanced validation and security
- **v1**: Stable version with basic validation
- **legacy**: Original endpoint for backwards compatibility

```typescript
// Use different API versions
const responseV2 = await client.submitActivity(activity, 'v2');
const responseV1 = await client.submitActivity(activity, 'v1');
const responseLegacy = await client.submitActivity(activity, 'legacy');
```

## OAuth2.0 Providers

The SDK supports multiple OAuth providers:

| Provider | Status | Use Case |
|----------|--------|----------|
| GitHub | Active | Internal testing and development |
| SolarEdge | Available | Production solar data integration |
| Custom | Extensible | Add your own OAuth provider |

### Provider-Specific Examples

```typescript
// GitHub OAuth (for testing)
const githubLogin = await client.oauthLogin('github');

// SolarEdge OAuth (for production)
const solarEdgeLogin = await client.oauthLogin('solaredge');
```

## Advanced Usage

### Batch Operations

```typescript
async function batchSubmit() {
  const client = new SilvanusClient({ apiKey: 'your-key' });
  
  const activities: ActivitySubmission[] = [
    { wallet_address: '0x...', activity_type: 'solar_export', value: 5.0 },
    { wallet_address: '0x...', activity_type: 'ev_charging', value: 3.0 },
    { wallet_address: '0x...', activity_type: 'energy_saving', value: 2.0 },
  ];
  
  // Submit all activities concurrently
  const promises = activities.map(activity => client.submitActivity(activity));
  const results = await Promise.all(promises);
  
  results.forEach(result => {
    console.log(`Transaction: ${result.txHash}`);
  });
}
```

### Custom Configuration

```typescript
// Configure timeout and retry behavior
const client = new SilvanusClient({
  apiKey: 'your-key',
  timeout: 60000,      // 60 second timeout
  maxRetries: 5        // 5 retry attempts
});
```

### Error Handling with Promise.allSettled

```typescript
async function robustBatchSubmit() {
  const client = new SilvanusClient({ apiKey: 'your-key' });
  
  const promises = activities.map(activity => client.submitActivity(activity));
  const results = await Promise.allSettled(promises);
  
  results.forEach((result, index) => {
    if (result.status === 'fulfilled') {
      console.log(`Activity ${index}: ${result.value.txHash}`);
    } else {
      console.log(`Activity ${index}: Failed - ${result.reason}`);
    }
  });
}
```

## Development

### Building the SDK

```bash
npm run build
```

### Running Tests

```bash
npm test
```

### Running Tests with Coverage

```bash
npm run test:coverage
```

### Code Quality

```bash
# Linting
npm run lint

# Type checking
npm run type-check

# Formatting
npm run format
```

### Examples

See the `examples/` directory for comprehensive usage examples:

- `basic-usage.ts` - API key authentication and basic operations
- `oauth-flow.ts` - OAuth2.0 authentication flow
- `async-usage.ts` - Advanced async patterns and error handling

## Migration Guide

### From Direct API Usage

**Before (Direct API):**
```typescript
import axios from 'axios';

const response = await axios.post(
  'https://silvanus-a4nt.onrender.com/v2/activities/submit',
  {
    wallet_address: '0x...',
    activity_type: 'solar_export',
    value: 5.0
  },
  {
    headers: { 'X-API-Key': 'your-key' }
  }
);
```

**After (SDK):**
```typescript
import { SilvanusClient, ActivitySubmission } from '@silvanus/sdk';

const client = new SilvanusClient({ apiKey: 'your-key' });
const activity: ActivitySubmission = {
  wallet_address: '0x...',
  activity_type: 'solar_export',
  value: 5.0
};
const response = await client.submitActivity(activity);
```

## Browser Usage

The SDK can be used in browser environments:

```html
<script type="module">
  import { SilvanusClient } from './dist/index.esm.js';
  
  const client = new SilvanusClient({
    apiKey: 'your-api-key'
  });
  
  // Use client...
</script>
```

## Node.js Usage

The SDK works seamlessly in Node.js environments:

```javascript
const { SilvanusClient } = require('@silvanus/sdk');

const client = new SilvanusClient({
  apiKey: process.env.SILVANUS_API_KEY
});
```

## Support

- **API Documentation**: See the main API README for detailed endpoint documentation
- **Issues**: Report issues on the GitHub repository
- **Examples**: Check the `examples/` directory for usage patterns

## License

This SDK is part of the Silvanus project and follows the same license terms.
