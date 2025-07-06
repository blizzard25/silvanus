const { ethers, upgrades } = require("hardhat");

async function main() {
  const silvanusTokenAddress = process.env.TOKEN_ADDRESS;
  const baseReward = ethers.parseEther("1");

  // Normalize and validate address
  const tokenAddressParsed = ethers.getAddress(silvanusTokenAddress);

  const Distributor = await ethers.getContractFactory("GreenRewardDistributor");

  // Deploy as an upgradeable proxy
  const distributor = await upgrades.deployProxy(
    Distributor,
    [tokenAddressParsed, baseReward],
    { initializer: "initialize" }
  );

  await distributor.waitForDeployment();

  console.log("✅ GreenRewardDistributor (proxy) deployed to:", await distributor.getAddress());
}

main().catch((error) => {
  console.error("❌ Deployment error:", error);
  process.exitCode = 1;
});
