require("dotenv").config();
const { ethers, upgrades, network } = require("hardhat");

function withTimeout(promise, ms, label) {
  let timeout = new Promise((_, reject) =>
    setTimeout(() => reject(new Error(`⏱ Timeout in step: ${label}`)), ms)
  );
  return Promise.race([promise, timeout]);
}

async function deployProxyWithErrorHandling(contractFactory, args, options, contractName) {
  try {
    console.log(`🚀 Deploying ${contractName} proxy...`);
    const contract = await upgrades.deployProxy(contractFactory, args, options);
    
    console.log(`⏳ Waiting for ${contractName} deployment...`);
    await contract.waitForDeployment();
    
    const address = await contract.getAddress();
    console.log(`✅ ${contractName} deployed at: ${address}`);
    
    return contract;
  } catch (error) {
    if (error.message && 
        error.message.includes('invalid value for value.to') && 
        error.message.includes('invalid address') &&
        error.code === 'INVALID_ARGUMENT') {
      
      console.warn(`⚠️  Detected ethers.js transaction formatting error during ${contractName} deployment`);
      console.warn("   This may indicate a successful deployment with formatting issues");
      console.warn("   Attempting to recover and verify deployment...");
      
      try {
        const address = await contract.getAddress();
        console.log(`🔍 Recovery attempt: Found contract at ${address}`);
        return contract;
      } catch (recoveryError) {
        console.error(`❌ Recovery failed for ${contractName}: ${recoveryError.message}`);
        throw new Error(`${contractName} deployment failed - unable to recover from formatting error`);
      }
    }
    
    console.error(`❌ ${contractName} deployment failed:`, error.message);
    throw error;
  }
}

async function verifyContractInitialization(contract, contractName, expectedChecks = {}) {
  try {
    const address = await contract.getAddress();
    console.log(`🔍 Verifying ${contractName} initialization at ${address}...`);
    
    if (expectedChecks.totalSupply) {
      const totalSupply = await contract.totalSupply();
      const expected = expectedChecks.totalSupply;
      
      if (totalSupply.toString() !== expected.toString()) {
        throw new Error(`${contractName} initialization failed: expected ${ethers.formatEther(expected)} tokens, got ${ethers.formatEther(totalSupply)}`);
      }
      
      console.log(`✅ ${contractName} total supply verified: ${ethers.formatEther(totalSupply)} tokens`);
    }
    
    if (expectedChecks.deployerBalance) {
      const deployerBalance = await contract.balanceOf(expectedChecks.deployerAddress);
      const expected = expectedChecks.deployerBalance;
      
      if (deployerBalance.toString() !== expected.toString()) {
        throw new Error(`${contractName} initialization failed: expected deployer balance ${ethers.formatEther(expected)} tokens, got ${ethers.formatEther(deployerBalance)}`);
      }
      
      console.log(`✅ ${contractName} deployer balance verified: ${ethers.formatEther(deployerBalance)} tokens`);
    }
    
    return true;
  } catch (error) {
    console.error(`❌ ${contractName} verification failed:`, error.message);
    throw error;
  }
}

async function main() {
  console.log("🔧 Starting Silvanus deployment script...");
  console.log("🌐 Network name:", network.name);
  console.log(`🌐 ENV Check — Alchemy Mainnet URL starts with: ${process.env.MAINNET_RPC_URL?.slice(0, 40)}...`);

  const [deployer] = await ethers.getSigners();
  if (!deployer || !deployer.address) {
    throw new Error("❌ No deployer signer found");
  }

  const deployerAddress = deployer.address;
  console.log("👤 Deployer address:", deployerAddress);

  const balance = await ethers.provider.getBalance(deployerAddress);
  console.log(`💰 Deployer balance: ${ethers.formatEther(balance)} ETH`);
  if (balance < ethers.parseEther("0.02")) {
    console.warn("⚠️ Deployer may have insufficient funds for mainnet deployment.");
  }

  let Silvanus;
  try {
    Silvanus = await ethers.getContractFactory("Silvanus");
    console.log("📦 Loaded Silvanus contract factory.");
    console.log("🧾 Contract bytecode size:", Silvanus.bytecode?.length);
    console.log("🧾 ABI function count:", Silvanus.interface?.fragments?.length);
  } catch (err) {
    console.error("❌ Failed to load contract factory:", err.message);
    throw err;
  }

  const tokenSymbol = "SVN";
  const decimals = 18;
  let initialSupply;
  try {
    const rawSupply = "100000000";
    initialSupply = ethers.parseUnits(rawSupply, decimals);
    if (typeof initialSupply !== "bigint" || initialSupply <= 0n) {
      throw new Error("initialSupply is invalid");
    }
    console.log("🧪 Initializer expects 1 arg(s): uint256 initialSupply");
    console.log(`✅ Parsed initial supply: ${initialSupply.toString()}`);
  } catch (err) {
    console.error("❌ Failed to parse initial supply:", err.message);
    throw err;
  }

  try {
    console.log("📐 Attempting to estimate gas for deployment...");
    if (upgrades.estimateGas && upgrades.estimateGas.deployProxy) {
      const estimatedGas = await upgrades.estimateGas.deployProxy(Silvanus, [initialSupply], {
        initializer: "initialize",
        kind: "uups",
      });
      console.log(`⛽ Estimated gas: ${estimatedGas.toString()}`);
    } else {
      console.log("⚠️ Gas estimation not available for deployProxy");
    }
  } catch (err) {
    console.warn("⚠️ Could not estimate gas:", err.message);
  }

  let silvanus;
  try {
    console.log("🚀 Step 1: Calling upgrades.deployProxy...");
    silvanus = await withTimeout(
      deployProxyWithErrorHandling(Silvanus, [initialSupply], {
        initializer: "initialize",
        kind: "uups",
      }, "Silvanus"),
      20000,
      "deployProxy"
    );
    console.log("✅ Step 2: deployProxy resolved");

    await verifyContractInitialization(silvanus, "Silvanus", {
      totalSupply: initialSupply,
      deployerBalance: initialSupply,
      deployerAddress: deployerAddress
    });

    const proxyAddress = await silvanus.getAddress();
    if (!ethers.isAddress(proxyAddress)) {
      throw new Error("Received invalid proxy address");
    }
    console.log(`✅ Silvanus proxy deployed at: ${proxyAddress}`);

    const implAddress = await upgrades.erc1967.getImplementationAddress(proxyAddress);
    console.log(`🔍 Implementation logic contract at: ${implAddress}`);
  } catch (err) {
    console.error("❌ Deployment or post-deployment check failed:");
    console.error(err.stack || err);
    throw err;
  }
}

main().catch((err) => {
  console.error("❌ Script terminated due to error:", err.message || err);
  process.exit(1);
});
