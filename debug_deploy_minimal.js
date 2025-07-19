const hre = require("hardhat");
const { ethers, upgrades } = hre;

async function main() {
  console.log("🔍 DEBUG: Testing Silvanus deployment with mainnet forking...\n");

  const [deployer] = await ethers.getSigners();
  const network = await ethers.provider.getNetwork();
  const balance = await ethers.provider.getBalance(deployer.address);

  console.log(`📡 Network: ${network.name} (Chain ID: ${network.chainId})`);
  console.log(`👤 Deployer: ${deployer.address}`);
  console.log(`💰 Balance: ${ethers.formatEther(balance)} ETH\n`);

  if (network.chainId === 1n) {
    console.warn("⚠️  WARNING: Using mainnet chainId=1 - this may cause OpenZeppelin state corruption!");
  } else {
    console.log("✅ Using safe hardhat network chainId for forking");
  }

  try {
    console.log("🪙 Testing Silvanus Token deployment...");
    
    const Silvanus = await ethers.getContractFactory("Silvanus");
    console.log("✅ Contract factory created successfully");
    
    console.log("Deploying proxy with parameters:");
    console.log(`  initialSupply: ${ethers.formatEther(ethers.parseEther("100000000"))} tokens`);
    console.log(`  initializer: "initialize"`);
    console.log(`  kind: "uups"`);
    
    const silvanus = await upgrades.deployProxy(Silvanus, [ethers.parseEther("100000000")], {
      initializer: "initialize",
      kind: "uups",
    });
    
    await silvanus.waitForDeployment();
    
    const silvanusAddress = await silvanus.getAddress();
    const silvanusImpl = await upgrades.erc1967.getImplementationAddress(silvanusAddress);
    
    console.log(`✅ SUCCESS: Silvanus deployed at: ${silvanusAddress}`);
    console.log(`   Logic implementation: ${silvanusImpl}`);
    
    const totalSupply = await silvanus.totalSupply();
    console.log(`   Total supply: ${ethers.formatEther(totalSupply)} SVN`);
    
    console.log("\n🎉 Local debugging deployment successful!");
    
  } catch (error) {
    console.error("❌ DEPLOYMENT FAILED!");
    console.error("Error details:", error);
    
    if (error.message.includes("invalid value for value.to")) {
      console.error("\n🔍 ANALYSIS: This is the exact error we're debugging!");
      console.error("Root cause: OpenZeppelin deployment state corruption");
      console.error("Solution: Clear .openzeppelin/ directory and avoid chainId=1");
    }
    
    throw error;
  }
}

main().catch((err) => {
  console.error("❌ DEBUG SCRIPT FAILED!");
  console.error(err);
  process.exit(1);
});
