# Environment Cleanup Instructions

## Issue Summary
The `deploy_all.js` script introduced persistent state corruption that caused all deployment scripts to hang indefinitely. This issue was resolved by:

1. Adding missing `kind: "uups"` parameter to all `upgrades.deployProxy()` calls
2. Using fresh shell environments to avoid corrupted state
3. Replacing the problematic all-in-one deployment approach with separate scripts

## CRITICAL: Mainnet Deployment State Corruption

Based on GitHub issue #346, OpenZeppelin stores deployment state in the `.openzeppelin/` directory. When `chainId: 1` is used with hardhat forking, subsequent deployments fail because the plugin tries to reuse deployment information that doesn't exist on the reset network, causing "invalid value for value.to" errors.

**Symptoms:**
- "invalid value for value.to (invalid address)" error during proxy deployment
- Failed contract creation transactions that consume gas but don't deploy contracts
- Deployment works on testnets but fails on mainnet

**Solution:**
1. Clear OpenZeppelin state before mainnet deployment:
   ```bash
   rm -rf .openzeppelin/
   npx hardhat clean
   ```

2. Use safe local debugging with mainnet forking:
   ```bash
   # Test deployment locally with mainnet forking
   npx hardhat run debug_deploy_minimal.js --config hardhat.config.debug.js
   ```

3. Avoid setting `chainId: 1` in hardhat forking configuration

## Mainnet Deployment Safety Checklist

**BEFORE attempting any mainnet deployment:**

1. **Clear deployment state:**
   ```bash
   rm -rf .openzeppelin/
   npx hardhat clean
   npx hardhat compile
   ```

2. **Test locally with mainnet forking:**
   ```bash
   npx hardhat run debug_deploy_minimal.js --config hardhat.config.debug.js
   ```

3. **Verify the test deployment succeeds multiple times**

4. **Double-check all parameters:**
   - Initial supply: `ethers.parseEther("100000000")` (100M tokens)
   - Proxy kind: `"uups"`
   - Gas settings: EIP-1559 with sufficient maxFeePerGas/maxPriorityFeePerGas

5. **Ensure sufficient ETH balance for deployment**

6. **Only proceed with mainnet deployment after local testing confirms success**

## Local Environment Cleanup Steps

### 1. Clear Hardhat Cache and OpenZeppelin State

**Linux/macOS:**
```bash
npx hardhat clean
rm -rf .openzeppelin/
```

**Windows Command Prompt:**
```cmd
npx hardhat clean
rmdir /s .openzeppelin
```

**Windows PowerShell:**
```powershell
npx hardhat clean
Remove-Item -Recurse -Force .openzeppelin
```

### 2. Clear Node.js Cache (if needed)

**All platforms:**
```bash
npm cache clean --force
# or if using yarn/pnpm
yarn cache clean
pnpm store prune
```

### 3. Reinstall Dependencies (if issues persist)

**Linux/macOS:**
```bash
rm -rf node_modules/
npm install
# or yarn install / pnpm install
```

**Windows Command Prompt:**
```cmd
rmdir /s node_modules
npm install
```

**Windows PowerShell:**
```powershell
Remove-Item -Recurse -Force node_modules
npm install
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
2. Clear OpenZeppelin state:
   - **Linux/macOS**: `rm -rf .openzeppelin/`
   - **Windows CMD**: `rmdir /s .openzeppelin`
   - **Windows PowerShell**: `Remove-Item -Recurse -Force .openzeppelin`
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

## Node.js Version Compatibility

**Important**: This project requires Node.js v20.17.0 or compatible versions due to micro-eth-signer dependencies.

### If you encounter ERR_REQUIRE_ESM errors:
1. Check your Node.js version: `node --version`
2. If using Node.js v20.17.0, ensure micro-eth-signer is pinned to version 0.14.0 in package.json
3. If using Node.js v20.19.0+, you can use newer micro-eth-signer versions

### Windows-specific fixes:
- Use the cleanup commands provided for your shell (CMD vs PowerShell)
- Ensure package-lock.json is deleted and regenerated after version changes
- After changing package.json dependencies, run:
  ```cmd
  del package-lock.json
  npm install
  ```

### ES Module Compatibility Fix:
If you see `Error [ERR_REQUIRE_ESM]: require() of ES Module` errors:
1. Delete package-lock.json and node_modules
2. Ensure micro-eth-signer is pinned to 0.14.0 in package.json dependencies
3. Reinstall dependencies with `npm install`

## Patch-Package Setup ✅ IMPLEMENTED

The ethers.js modifications are now permanent using `patch-package`. The setup is complete and patches are automatically applied after `npm install`.

**What's Included:**
- `patch-package` installed as dev dependency
- Patch file: `patches/@nomicfoundation+hardhat-ethers+3.0.9.patch`
- Automatic patch application via `postinstall` script in package.json

**For New Developers:**
1. Clone repository: `git clone <repo>`
2. Install dependencies: `npm install` (patches auto-apply)
3. Verify patches: Look for "Applying patches..." message during install
4. Deploy: `npx hardhat run scripts/deploy_all.js --network mainnet`

**Maintenance Notes:**
- Patches are specific to `@nomicfoundation/hardhat-ethers@3.0.9`
- If upgrading this package, patches may need regeneration
- To regenerate patches: modify node_modules files, then run `npx patch-package @nomicfoundation/hardhat-ethers`

## Success Criteria
- `deploy.js` completes in ~20 seconds ✅
- `deploy_distributor.js` completes in ~20 seconds  
- `fund_all.js` successfully distributes tokens without hanging
- No persistent hanging issues across multiple script runs
- No ERR_REQUIRE_ESM errors on Windows with Node.js v20.17.0
- Patch-package automatically applies ethers.js fixes ✅
- Mainnet deployment succeeds without "invalid address" errors ✅
