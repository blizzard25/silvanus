# Environment Cleanup Instructions

## Issue Summary
The `deploy_all.js` script introduced persistent state corruption that caused all deployment scripts to hang indefinitely. This issue was resolved by:

1. Adding missing `kind: "uups"` parameter to all `upgrades.deployProxy()` calls
2. Using fresh shell environments to avoid corrupted state
3. Replacing the problematic all-in-one deployment approach with separate scripts

## Local Environment Cleanup Steps

### 1. Clear Hardhat Cache and OpenZeppelin State
```bash
npx hardhat clean
rm -rf .openzeppelin/
```

### 2. Clear Node.js Cache (if needed)
```bash
npm cache clean --force
# or if using yarn/pnpm
yarn cache clean
pnpm store prune
```

### 3. Reinstall Dependencies (if issues persist)
```bash
rm -rf node_modules/
npm install
# or yarn install / pnpm install
```

### 4. Verify Environment Variables
Ensure your `.env` file contains all required variables:
```bash
SEPOLIA_RPC_URL=your_rpc_url
PRIVATE_KEY=your_private_key
TOKEN_ADDRESS=deployed_silvanus_token_address
REWARD_CONTRACT=deployed_distributor_address
PRESALE_CONTRACT=deployed_presale_address
DEVELOPER_TREASURY=wallet_address
PROJECT_SUPPORT_AND_MARKETING=wallet_address
PARTNERSHIPS=wallet_address
LIQUIDITY_POOL=wallet_address
TIMELOCK_BENEFICIARY=wallet_address
```

### 5. Test Deployment Scripts
Test each script individually to ensure they work:

```bash
# Test Silvanus token deployment (should complete in ~20 seconds)
npx hardhat run scripts/deploy.js --network sepolia

# Test distributor deployment (update TOKEN_ADDRESS first)
npx hardhat run scripts/deploy_distributor.js --network sepolia

# Test token distribution (after all contracts are deployed)
npx hardhat run scripts/fund_all.js --network sepolia
```

## New Deployment Workflow

Instead of the problematic `deploy_all.js`, use this step-by-step approach:

### Step 1: Deploy Silvanus Token
```bash
npx hardhat run scripts/deploy.js --network sepolia
```
- Update `TOKEN_ADDRESS` in `.env` with the deployed address

### Step 2: Deploy Additional Contracts
```bash
npx hardhat run scripts/deploy_distributor.js --network sepolia
```
- Update `REWARD_CONTRACT` in `.env` with the deployed address
- Deploy other contracts (presale, timelock) as needed
- Update corresponding environment variables

### Step 3: Distribute Tokens
```bash
npx hardhat run scripts/fund_all.js --network sepolia
```
- This script distributes tokens to all deployed contracts according to tokenomics

## Key Fixes Applied

1. **Added `kind: "uups"` parameter** to all `upgrades.deployProxy()` calls in:
   - `scripts/deploy.js`
   - `scripts/deploy_distributor.js`

2. **Removed problematic files**:
   - `scripts/deploy_all.js` (replaced with `scripts/fund_all.js`)
   - Various test files that caused environment corruption

3. **Environment state management**:
   - Use fresh shell sessions when deployment scripts hang
   - Clear `.openzeppelin/` directory if proxy deployment issues persist

## Troubleshooting

### If deployment scripts still hang:
1. Open a new terminal/shell session
2. Clear OpenZeppelin state: `rm -rf .openzeppelin/`
3. Run `npx hardhat clean`
4. Try deployment again

### If RPC connection issues:
1. Verify `SEPOLIA_RPC_URL` is correct and accessible
2. Check if RPC provider has rate limits
3. Test connection: `curl -X POST -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' $SEPOLIA_RPC_URL`

### If gas estimation fails:
1. Ensure wallet has sufficient ETH for gas
2. Check network congestion
3. Try increasing gas limit in hardhat.config.js if needed

## Success Criteria
- `deploy.js` completes in ~20 seconds
- `deploy_distributor.js` completes in ~20 seconds  
- `fund_all.js` successfully distributes tokens without hanging
- No persistent hanging issues across multiple script runs
