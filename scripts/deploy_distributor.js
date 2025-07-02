const { ethers } = require("hardhat");

async function main() {
  const silvanusTokenAddress = process.env.TOKEN_ADDRESS;
  const baseReward = ethers.parseEther("1"); // 1 SVN as base reward
  const tokenAddressParsed = ethers.getAddress(silvanusTokenAddress); // resolves it properly

  const Distributor = await ethers.getContractFactory("GreenRewardDistributor");
  const distributor = await Distributor.deploy(tokenAddressParsed, baseReward);
  await distributor.waitForDeployment();

  console.log("GreenRewardDistributor deployed to:", await distributor.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
