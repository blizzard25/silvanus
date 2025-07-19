require("dotenv").config();
const { ethers, upgrades, network } = require("hardhat");

async function main() {
  console.log("🔧 Starting Silvanus deployment script...");
  console.log("🌐 Network name:", network.name);

  // Get deployer signer
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

  // Load contract factory
  let Silvanus;
  try {
    Silvanus = await ethers.getContractFactory("Silvanus");
    console.log("📦 Loaded Silvanus contract factory.");
  } catch (err) {
    console.error("❌ Failed to load contract factory:", err.message);
    throw err;
  }

  // Parse initial supply
  const tokenSymbol = "SVN";
  const decimals = 18;
  let initialSupply;
  try {
    const rawSupply = "100000000"; // 100 million
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

  // Try estimating gas
  try {
    console.log("📐 Attempting to estimate gas for deployment...");
    const estimatedGas = await upgrades.estimateGas.deployProxy(Silvanus, [initialSupply], {
      initializer: "initialize",
      kind: "uups",
    });
    console.log(`⛽ Estimated gas: ${estimatedGas.toString()}`);
  } catch (err) {
    console.warn("⚠️ Could not estimate gas:", err.message);
  }

  // Deploy proxy contract
  let silvanus;
  try {
    console.log("🚀 Deploying Silvanus contract via proxy...");
    silvanus = await upgrades.deployProxy(Silvanus, [initialSupply], {
      initializer: "initialize",
      kind: "uups",
    });

    await silvanus.waitForDeployment();
    const proxyAddress = await silvanus.getAddress();
    if (!ethers.isAddress(proxyAddress)) {
      throw new Error("Received invalid proxy address");
    }
    console.log(`✅ Silvanus proxy deployed at: ${proxyAddress}`);

    // Implementation contract address
    const implAddress = await upgrades.erc1967.getImplementationAddress(proxyAddress);
    console.log(`🔍 Implementation logic contract at: ${implAddress}`);

    // Verify deployer's token balance
    const balance = await silvanus.balanceOf(deployerAddress);
    console.log(`💰 Deployer token balance: ${ethers.formatUnits(balance, decimals)} ${tokenSymbol}`);
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
