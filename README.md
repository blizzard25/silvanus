# Silvanus Project

[![Website](https://img.shields.io/badge/Website-silvanusproject.com-green)](https://silvanusproject.com)
[![API Status](https://img.shields.io/badge/API-Live-brightgreen)](https://silvanus-a4nt.onrender.com/healthz)
[![License](https://img.shields.io/badge/License-ISC-blue.svg)](LICENSE)

Silvanus is a revolutionary cryptocurrency focusing on greenchain solutions that incentivizes environmental sustainability through blockchain technology. Instead of using energy-intensive proof-of-work (PoW) mining methods, Silvanus relies on **proof-of-green (PoG)** to mint new tokens, rewarding users for actions that reduce their carbon footprint.

## 🌱 What is Proof-of-Green?

Proof-of-Green (PoG) is our innovative consensus mechanism that rewards real-world environmental actions:

- **Commercial Energy Production**: Clean energy producers generate SVN tokens to use as liqudity/secondary income as replacements to centralized Renewable Energy Credits
- **Solar Energy Export**: Earn SVN tokens for excess solar power fed back to the grid
- **EV Charging**: Get rewarded for charging electric vehicles with clean energy
- **Regenerative Braking**: Receive tokens for energy recovered through EV regenerative braking
- **Smart Thermostat Usage**: Earn rewards for energy-efficient temperature management

## 🏗️ Project Architecture

```
silvanus/
├── api/                    # FastAPI backend with versioned endpoints
│   ├── routes/            # API route handlers (v1, v2, legacy)
│   ├── auth.py           # API key authentication system
│   ├── validation.py     # Input validation and security
│   ├── blockchain_guard.py # Blockchain transaction security
│   └── main.py           # FastAPI application entry point
├── contracts/             # Ethereum smart contracts
│   ├── Silvanus.sol      # Main SVN token contract
│   ├── GreenRewardDistributor.sol # Reward calculation logic
│   ├── SVNPresale.sol    # Token presale contract
│   └── TokenTimelock.sol # Token vesting contract
├── scripts/              # Deployment and interaction scripts
├── test/                 # Smart contract test suites
└── python/               # Python utilities and testing tools
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v16 or higher)
- **Python** (3.8 or higher)
- **Git**
- **Ethereum wallet** (MetaMask recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/blizzard25/silvanus.git
   cd silvanus
   ```

2. **Install smart contract dependencies**
   ```bash
   npm install
   ```

3. **Install Python API dependencies**
   ```bash
   cd api
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# Blockchain Configuration
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
PRIVATE_KEY=your_private_key_here
REWARD_CONTRACT=0x...
TOKEN_ADDRESS=0x...

# API Configuration
API_KEYS=key1,key2,key3
DATABASE_URL=sqlite:///./silvanus.db

# Wallet Addresses
RECIPIENT_WALLET_ADDRESS=0x...
DIS_WALLET_ADDRESS=0x...
TIMELOCK_BENEFICIARY=0x...
```

## 🔧 Development

### Smart Contract Development

```bash
# Compile contracts
npx hardhat compile

# Run tests
npx hardhat test

# Deploy to Sepolia testnet
npx hardhat run scripts/deploy.js --network sepolia
```

### API Development

```bash
cd api

# Start development server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run API tests
python python/test_rewards_api.py
```

### Testing Your Setup

1. **Test API health**
   ```bash
   curl http://localhost:8000/healthz
   ```

2. **Submit a test activity**
   ```bash
   curl -X POST "http://localhost:8000/v2/activities/submit" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: YOUR_API_KEY" \
     -d '{
       "wallet_address": "0x...",
       "activity_type": "solar_export",
       "value": 5.0,
       "details": {"note": "Test solar export"}
     }'
   ```

## 📡 API Endpoints

The Silvanus API provides versioned endpoints for submitting green energy activities:

- **V2 (Recommended)**: `/v2/activities/submit` - Latest features with enhanced validation
- **V1**: `/v1/activities/submit` - Stable version with basic validation  
- **Legacy**: `/activities/submit` - Backward compatibility (deprecated)

### Authentication

All API requests require an API key:

```bash
Header: X-API-Key: YOUR_API_KEY
```

### Rate Limiting

- **1000 requests per hour** per API key
- Rate limits apply across all endpoints
- 422 status code returned when limits exceeded

For detailed API documentation, see [api/README.md](api/README.md).

## 🔐 Security Features

Silvanus implements multiple layers of security:

- **Blockchain Guard**: Prevents token distribution on validation failures
- **Input Validation**: Comprehensive Pydantic model validation
- **Rate Limiting**: Protection against API abuse
- **Request Size Limits**: Prevents oversized payload attacks
- **Security Logging**: Comprehensive audit trail
- **API Key Authentication**: Secure access control

## 🏦 Smart Contracts

### Silvanus Token (SVN)

- **Network**: Ethereum Sepolia Testnet
- **Type**: ERC-20 with upgradeable proxy pattern
- **Features**: Burn mechanism redirects to grant wallet instead of destroying tokens

### Green Reward Distributor

Calculates token rewards using logarithmic diminishing returns:

```solidity
adjustedReward = (score * baseReward) / log10(totalEvents + 10)
```

- **Score**: Raw kWh value from activity
- **Base Reward**: 1 SVN = 1e18 wei
- **Diminishing Returns**: Prevents reward farming

### Presale Contract

- **Token Distribution**: Manages initial token sale
- **Vesting**: Time-locked token release schedule
- **Whitelist**: Controlled access to presale participation

## 🌍 Supported Activities

| Activity Type | Description | Reward Calculation |
|---------------|-------------|-------------------|
| `solar_export` | Power exported to grid from solar panels | kWh × reward multiplier |
| `wind_export` | Power exported to grid from wind turbine generation | kWh × reward multiplier |
| `ev_charging` | EV charging with clean/off-peak energy | kWh × reward multiplier |
| `regen_braking` | Energy recovered through regenerative braking | kWh × reward multiplier |
| `thermostat_adjustment` | Smart thermostat energy savings | kWh × reward multiplier |

## 📊 Transaction Explorer

Monitor real-time token distributions at [silvanusproject.com](https://silvanusproject.com) in the Transaction Explorer section. Transactions typically appear within 30 seconds of submission.

## 🧪 Testing

### Smart Contract Tests

```bash
# Run all contract tests
npx hardhat test

# Run specific test file
npx hardhat test test/Silvanus.test.js
```

### API Tests

```bash
# Comprehensive API test suite
python python/test_rewards_api.py

# Test specific endpoint
curl -X GET "http://localhost:8000/activities/types"
```

## 🚀 Deployment

### Smart Contracts

```bash
# Deploy to Sepolia testnet
npx hardhat run scripts/deploy.js --network sepolia

# Upgrade existing contracts
npx hardhat run scripts/upgrade-silvanus.js --network sepolia
```

### API Deployment

The API is deployed on [Render](https://render.com) and automatically deploys from the main branch.

**Live API**: https://silvanus-a4nt.onrender.com

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow existing code patterns and conventions
- Add comprehensive tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PRs

## 📄 License

This project is licensed under the ISC License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Website**: [silvanusproject.com](https://silvanusproject.com)
- **Email**: support@silvanusproject.com
- **GitHub Issues**: [Report bugs and request features](https://github.com/blizzard25/silvanus/issues)

## 🔗 Links

- **Live API**: https://silvanus-a4nt.onrender.com
- **Transaction Explorer**: https://silvanusproject.com
- **Sepolia Testnet**: https://sepolia.etherscan.io/
- **OpenZeppelin Contracts**: https://docs.openzeppelin.com/contracts/

---

**Built for a sustainable future** 🌍
