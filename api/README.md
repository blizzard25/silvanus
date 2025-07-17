
# Silvanus API Documentation

[![API Status](https://img.shields.io/badge/API-Live-brightgreen)](https://silvanus-a4nt.onrender.com/healthz)
[![Version](https://img.shields.io/badge/Version-2.0-blue)](https://silvanus-a4nt.onrender.com)

The Silvanus API enables users to submit green energy activity data and receive $SVN token rewards on-chain. This FastAPI-based system directly interacts with smart contracts deployed on Ethereum Sepolia Testnet, providing a secure and scalable platform for proof-of-green token distribution.

**Live API**: https://silvanus-a4nt.onrender.com

---

## 🔐 Authentication

The Silvanus API supports two authentication methods:

### API Key Authentication (Traditional)

```http
Header: X-API-Key: YOUR_API_KEY
```

### OAuth2.0 Authentication (Recommended)

```http
Header: Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Security Features:**
- Dual authentication support (API keys + OAuth2.0)
- PKCE (Proof Key for Code Exchange) for secure authorization
- State parameter validation for CSRF protection
- JWT-based access tokens with expiration
- Token refresh capabilities
- Rate limiting per user identity (1000 requests/hour)
- Request size limits (1MB maximum)
- Comprehensive security logging

---

## 🔑 OAuth2.0 Flow

### Step 1: Initiate OAuth Login

#### `GET /oauth/login/github?user_id={user_id}`

Start the OAuth2.0 authorization flow with GitHub.

**Parameters:**
- `user_id` (required): Unique identifier for the user session

**Response:**
```json
{
  "auth_url": "https://github.com/login/oauth/authorize?client_id=...&code_challenge=...&state=...",
  "state": "PlB5gZGHoTfpqwbdFfu80R_EZF9H_YeXZut-WjWpJzk",
  "session_key": "user123",
  "provider": "github"
}
```

**Usage:**
1. Redirect user to the `auth_url`
2. Store the `state` parameter for validation
3. User completes GitHub authorization

### Step 2: Handle OAuth Callback

#### `GET /oauth/callback/github?code={code}&state={state}`

Exchange authorization code for access token.

**Parameters:**
- `code` (required): Authorization code from GitHub
- `state` (required): State parameter for CSRF validation

**Response (Success):**
```json
{
  "access_token": "gho_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "ghr_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "wallet_address": "0x..."
}
```

**Response (Error):**
```json
{
  "error": "invalid_grant",
  "error_description": "The provided authorization grant is invalid"
}
```

### Step 3: Use Access Token

Include the access token in API requests:

```http
Authorization: Bearer gho_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### OAuth2.0 Test Endpoints

For development and testing purposes:

#### `POST /oauth/test/store-token`
Store a test OAuth token for development.

#### `GET /oauth/test/list-tokens`
List all stored OAuth tokens (development only).

### Token Management

- **Access Token Lifetime**: 1 hour (3600 seconds)
- **Refresh Token**: Available for token renewal
- **Token Storage**: Secure database storage with expiration tracking
- **Token Validation**: Automatic expiration checking on each request

### Client Implementation Examples

#### Python Client

```python
import requests
import json

class SilvanusOAuthClient:
    def __init__(self, base_url="https://silvanus-a4nt.onrender.com"):
        self.base_url = base_url
        self.access_token = None
    
    def initiate_login(self, user_id):
        """Step 1: Get OAuth authorization URL"""
        response = requests.get(f"{self.base_url}/oauth/login/github", 
                              params={"user_id": user_id})
        return response.json()
    
    def exchange_code(self, code, state):
        """Step 2: Exchange authorization code for access token"""
        response = requests.get(f"{self.base_url}/oauth/callback/github",
                              params={"code": code, "state": state})
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            return token_data
        return response.json()
    
    def submit_activity(self, wallet_address, activity_type, value):
        """Submit activity using OAuth2.0 bearer token"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {
            "wallet_address": wallet_address,
            "activity_type": activity_type,
            "value": value
        }
        response = requests.post(f"{self.base_url}/v2/activities/submit",
                               json=data, headers=headers)
        return response.json()

# Usage
client = SilvanusOAuthClient()
auth_data = client.initiate_login("user123")
print(f"Visit: {auth_data['auth_url']}")
# After user authorization, exchange code for token
# token_data = client.exchange_code(code, state)
# result = client.submit_activity("0x...", "solar_export", 5.0)
```

#### JavaScript Client

```javascript
class SilvanusOAuthClient {
    constructor(baseUrl = "https://silvanus-a4nt.onrender.com") {
        this.baseUrl = baseUrl;
        this.accessToken = null;
    }
    
    async initiateLogin(userId) {
        // Step 1: Get OAuth authorization URL
        const response = await fetch(`${this.baseUrl}/oauth/login/github?user_id=${userId}`);
        return await response.json();
    }
    
    async exchangeCode(code, state) {
        // Step 2: Exchange authorization code for access token
        const response = await fetch(`${this.baseUrl}/oauth/callback/github?code=${code}&state=${state}`);
        if (response.ok) {
            const tokenData = await response.json();
            this.accessToken = tokenData.access_token;
            return tokenData;
        }
        return await response.json();
    }
    
    async submitActivity(walletAddress, activityType, value) {
        // Submit activity using OAuth2.0 bearer token
        const response = await fetch(`${this.baseUrl}/v2/activities/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.accessToken}`
            },
            body: JSON.stringify({
                wallet_address: walletAddress,
                activity_type: activityType,
                value: value
            })
        });
        return await response.json();
    }
}

// Usage
const client = new SilvanusOAuthClient();
const authData = await client.initiateLogin("user123");
console.log(`Visit: ${authData.auth_url}`);
// After user authorization, exchange code for token
// const tokenData = await client.exchangeCode(code, state);
// const result = await client.submitActivity("0x...", "solar_export", 5.0);
```

---

## 📊 API Versioning

The Silvanus API supports multiple versions for backward compatibility:

| Version | Endpoint Prefix | Status | Features |
|---------|----------------|--------|----------|
| **V2** | `/v2/` | ✅ **Recommended** | Enhanced validation, security features |
| **V1** | `/v1/` | ✅ Stable | Basic validation, reliable |
| **Legacy** | `/` | ⚠️ Deprecated | Backward compatibility only |

### Version Differences

- **V2**: Latest security features, comprehensive validation, blockchain guard protection
- **V1**: Stable version with essential validation
- **Legacy**: Maintains backward compatibility, will be removed in future versions

---

## 🌱 Green Activity Submission

### V2 Endpoint (Recommended)

#### `POST /v2/activities/submit`

Submit a green energy activity with enhanced validation and security.

**Request Headers:**
```http
Content-Type: application/json
X-API-Key: YOUR_API_KEY
```

**Request Body:**
```json
{
  "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
  "activity_type": "solar_export",
  "value": 5.0,
  "details": {
    "note": "Solar panel export during peak production",
    "platform": "Raspberry Pi 4",
    "timestamp": "2025-07-17T14:30:00Z",
    "location": "California, USA"
  }
}
```

**Response (Success - 200):**
```json
{
  "txHash": "0xabc123def456789...",
  "status": "confirmed"
}
```

**Response (Validation Error - 422):**
```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "value"],
      "msg": "Input should be less than or equal to 10000",
      "input": 15000.0,
      "ctx": {"le": 10000.0}
    }
  ]
}
```

### V1 Endpoint

#### `POST /v1/activities/submit`

Stable version with basic validation.

**Request/Response**: Same format as V2, but with less comprehensive validation.

### Legacy Endpoint

#### `POST /activities/submit`

**⚠️ Deprecated**: Use V2 or V1 endpoints for new integrations.

---

## 📋 Input Validation

### Activity Submission Model

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `wallet_address` | `string` | Valid Ethereum address | Recipient wallet for token rewards |
| `activity_type` | `string` | Must be supported type | Type of green activity |
| `value` | `float` | 0.0 ≤ value ≤ 10000.0 | Energy value in kWh |
| `details` | `object` | Optional | Additional activity metadata |

### Validation Rules

- **Wallet Address**: Must be valid Ethereum address format (checksummed)
- **Activity Type**: Must be one of the supported types (see Activity Types section)
- **Value Range**: 0.0 to 10000.0 kWh (prevents abuse and ensures realistic values)
- **Details**: Optional object for additional context and diagnostics

### Security Validation

The API implements a **Blockchain Guard** system that:
- Validates all inputs before blockchain execution
- Prevents token distribution on validation failures
- Ensures atomic validation and transaction processing
- Provides comprehensive error reporting

---

## 🎯 Supported Activity Types

### `GET /activities/types`

Returns the current list of supported green activities.

**Response:**
```json
[
  {
    "type": "solar_export",
    "description": "Power exported to grid from solar array",
    "expectedDetails": ["kWhExported", "panelEfficiency", "weatherConditions"]
  },
  {
    "type": "ev_charging",
    "description": "Charging EV using solar or off-peak grid power",
    "expectedDetails": ["kWhUsed", "chargingDuration", "offPeak", "vehicleModel"]
  },
  {
    "type": "regen_braking",
    "description": "Energy recovered through regenerative braking",
    "expectedDetails": ["kWhRecovered", "distance", "terrain"]
  },
  {
    "type": "thermostat_adjustment",
    "description": "Smart thermostat behavior changes to save energy",
    "expectedDetails": ["targetTemp", "ecoMode", "duration", "energySaved"]
  }
]
```

### Activity Type Details

#### Solar Export (`solar_export`)
- **Purpose**: Reward excess solar energy fed back to the grid
- **Measurement**: kWh exported
- **Typical Range**: 0.1 - 50.0 kWh per submission

#### EV Charging (`ev_charging`)
- **Purpose**: Incentivize clean energy vehicle charging
- **Measurement**: kWh consumed during charging
- **Typical Range**: 5.0 - 100.0 kWh per session

#### Regenerative Braking (`regen_braking`)
- **Purpose**: Reward energy recovery during vehicle operation
- **Measurement**: kWh recovered through regenerative systems
- **Typical Range**: 0.1 - 5.0 kWh per trip

#### Thermostat Adjustment (`thermostat_adjustment`)
- **Purpose**: Encourage energy-efficient temperature management
- **Measurement**: kWh saved through smart adjustments
- **Typical Range**: 0.5 - 10.0 kWh per day

---

## ⛓️ Blockchain Integration

### Smart Contract Interaction

The API interacts with the following smart contracts on Ethereum Sepolia:

#### GreenRewardDistributor Contract
- **Function**: `reward(address user, uint256 score)`
- **Purpose**: Calculates and distributes SVN tokens
- **Gas Limit**: 300,000 gas per transaction
- **Fee Strategy**: EIP-1559 with dynamic pricing

#### Reward Calculation Formula

```solidity
adjustedReward = (score * baseReward) / log10(totalEvents + 10)
```

**Parameters:**
- `score`: kWh value × 100 (scaled for precision)
- `baseReward`: 1 SVN = 1e18 wei
- `totalEvents`: Running count of all reward events
- `log10`: Logarithmic diminishing returns to prevent farming

**Example Calculation:**
```
Activity: 5.0 kWh solar export
Score: 5.0 × 100 = 500
Base Reward: 1e18 wei (1 SVN)
Total Events: 1000
Adjusted Reward: (500 × 1e18) / log10(1010) ≈ 166 SVN
```

### Transaction Processing

1. **Validation**: Input validation and security checks
2. **Authorization**: Blockchain guard authorization
3. **Transaction Building**: EIP-1559 transaction construction
4. **Signing**: Private key transaction signing
5. **Submission**: Raw transaction broadcast to network
6. **Confirmation**: Receipt polling with 30-second timeout

### Gas Management

- **Gas Limit**: 300,000 gas per reward transaction
- **Max Fee**: 25 gwei
- **Priority Fee**: 2 gwei
- **Network**: Ethereum Sepolia Testnet (Chain ID: 11155111)

---

## 🛡️ Security Features

### Blockchain Guard System

The API implements a comprehensive security system:

```python
@blockchain_protected
async def submit_activity(activity: ActivitySubmission, guard=None):
    # Validation occurs before any blockchain interaction
    guard.validate_activity(activity)  # Throws 422 on failure
    guard.allow_blockchain()           # Authorizes blockchain execution
    # Blockchain transaction only executes after validation
```

### Security Layers

1. **Input Validation**: Pydantic model validation with custom constraints
2. **Authentication**: API key verification
3. **Rate Limiting**: 1000 requests/hour per API key
4. **Request Size Limits**: 1MB maximum payload size
5. **Blockchain Guard**: Prevents token distribution on validation failures
6. **Security Logging**: Comprehensive audit trail
7. **Error Handling**: Secure error responses without sensitive data exposure

### Rate Limiting

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642694400
```

**Rate Limit Exceeded (429):**
```json
{
  "error": "Rate limit exceeded",
  "detail": "1000 per 1 hour"
}
```

---

## 📈 Response Codes

| Code | Status | Description |
|------|--------|-------------|
| `200` | Success | Activity submitted and tokens distributed |
| `400` | Bad Request | Invalid request format |
| `401` | Unauthorized | Missing or invalid API key |
| `422` | Validation Error | Input validation failed |
| `429` | Rate Limited | Too many requests |
| `500` | Server Error | Internal server or blockchain error |

### Error Response Format

```json
{
  "detail": "Error description",
  "type": "error_type",
  "loc": ["field", "location"],
  "input": "invalid_value"
}
```

---

## 🔍 Health Check & Monitoring

### Health Check Endpoint

#### `GET /healthz`

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-17T14:30:00Z",
  "version": "2.0.0"
}
```

### API Monitoring

- **Uptime**: 99.9% SLA on Render platform
- **Response Time**: < 500ms average
- **Transaction Confirmation**: 30-second timeout
- **Error Rate**: < 0.1% for valid requests

---

## 🧪 Testing

### Local Testing

```bash
# Start local API server
cd api
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Test health endpoint
curl http://localhost:8000/healthz

# Test activity submission
curl -X POST "http://localhost:8000/v2/activities/submit" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "wallet_address": "0x...",
    "activity_type": "solar_export",
    "value": 5.0,
    "details": {"note": "Test submission"}
  }'
```

### Test Suite

```bash
# Run comprehensive API tests
python python/test_rewards_api.py

# Expected output:
# ✅ Health Check: PASS
# ✅ Activity Types: PASS  
# ✅ V1 Endpoint: PASS
# ✅ V2 Endpoint: PASS
# ✅ Legacy Endpoint: PASS
# Overall: 5/5 tests passed
```

### Validation Testing

```bash
# Test validation limits
curl -X POST "http://localhost:8000/v2/activities/submit" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "wallet_address": "0x...",
    "activity_type": "solar_export",
    "value": 15000.0,
    "details": {"note": "Should fail validation"}
  }'

# Expected: 422 Validation Error
```

---

## 🚀 Deployment

### Production Environment

- **Platform**: Render.com
- **URL**: https://silvanus-a4nt.onrender.com
- **Auto-Deploy**: Enabled from main branch
- **Environment**: Python 3.12, FastAPI, Uvicorn

### Environment Variables

```env
# Required for production deployment
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/PROJECT_ID
PRIVATE_KEY=0x...
REWARD_CONTRACT=0x...
API_KEYS=key1,key2,key3
DATABASE_URL=postgresql://...
```

### Deployment Process

1. **Code Push**: Push to main branch
2. **Auto-Build**: Render automatically builds from main
3. **Health Check**: Automated health verification
4. **Live Deployment**: Zero-downtime deployment
5. **Monitoring**: Continuous uptime monitoring

---

## 📚 API Client Examples

### Python Client

```python
import requests

class SilvanusClient:
    def __init__(self, api_key, base_url="https://silvanus-a4nt.onrender.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }
    
    def submit_activity(self, wallet_address, activity_type, value, details=None):
        payload = {
            "wallet_address": wallet_address,
            "activity_type": activity_type,
            "value": value,
            "details": details or {}
        }
        
        response = requests.post(
            f"{self.base_url}/v2/activities/submit",
            json=payload,
            headers=self.headers
        )
        
        return response.json()

# Usage
client = SilvanusClient("your_api_key")
result = client.submit_activity(
    wallet_address="0x...",
    activity_type="solar_export",
    value=5.0,
    details={"note": "Morning solar production"}
)
print(f"Transaction: {result['txHash']}")
```

### JavaScript Client

```javascript
class SilvanusClient {
    constructor(apiKey, baseUrl = 'https://silvanus-a4nt.onrender.com') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
    }
    
    async submitActivity(walletAddress, activityType, value, details = {}) {
        const response = await fetch(`${this.baseUrl}/v2/activities/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': this.apiKey
            },
            body: JSON.stringify({
                wallet_address: walletAddress,
                activity_type: activityType,
                value: value,
                details: details
            })
        });
        
        return await response.json();
    }
}

// Usage
const client = new SilvanusClient('your_api_key');
const result = await client.submitActivity(
    '0x...',
    'ev_charging',
    25.0,
    { note: 'Overnight charging session' }
);
console.log(`Transaction: ${result.txHash}`);
```

---

## 🔄 Migration Guide

### Migrating from Legacy to V2

**Legacy Endpoint:**
```bash
POST /activities/submit
```

**V2 Endpoint:**
```bash
POST /v2/activities/submit
```

**Changes:**
- Enhanced input validation
- Improved error messages
- Blockchain guard protection
- Better security logging

**Migration Steps:**
1. Update endpoint URL to include `/v2/`
2. Ensure wallet addresses are properly checksummed
3. Validate activity values are within 0.0-10000.0 range
4. Update error handling for new 422 response format

---

## 📞 Support & Contact

### Getting Help

- **Documentation**: This README and inline API docs
- **GitHub Issues**: [Report bugs and request features](https://github.com/blizzard25/silvanus/issues)
- **Email Support**: support@silvanusproject.com

### Common Issues

#### Authentication Errors
```json
{"detail": "Invalid API key"}
```
**Solution**: Verify your API key is correct and included in the `X-API-Key` header.

#### Validation Errors
```json
{"detail": [{"type": "less_than_equal", "loc": ["body", "value"], "msg": "Input should be less than or equal to 10000"}]}
```
**Solution**: Ensure activity values are within the 0.0-10000.0 kWh range.

#### Rate Limiting
```json
{"error": "Rate limit exceeded", "detail": "1000 per 1 hour"}
```
**Solution**: Reduce request frequency or contact support for higher limits.

### Feature Requests

We welcome feature requests and contributions! Please:
1. Check existing GitHub issues
2. Create detailed feature request with use case
3. Consider contributing via pull request

---

## 📄 API Changelog

### Version 2.0 (Current)
- ✅ Enhanced input validation with Pydantic models
- ✅ Blockchain guard security system
- ✅ Comprehensive error handling
- ✅ Security logging and monitoring
- ✅ Rate limiting improvements

### Version 1.0
- ✅ Basic activity submission
- ✅ Smart contract integration
- ✅ API key authentication
- ✅ Activity type validation

### Legacy
- ⚠️ Deprecated - use V1 or V2
- Basic functionality maintained for backward compatibility

---

**Built for a sustainable future** 🌍
