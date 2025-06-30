const { ethers } = require("hardhat");

async function main() {
  const silvanusTokenAddress = "0x3fcE4d2E8bfF26732EAAf942B67bF31a1e5a965d";
  const tokenAddressParsed = ethers.getAddress(silvanusTokenAddress); // resolves it properly

  const Distributor = await ethers.getContractFactory("GreenRewardDistributor");
  const distributor = await Distributor.deploy(tokenAddressParsed);
  await distributor.waitForDeployment();

  console.log("GreenRewardDistributor deployed to:", await distributor.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
