const { ethers } = require("hardhat");

async function main() {
  const distributorAddress = process.env.REWARD_CONTRACT;
  const distributor = await ethers.getContractAt("GreenRewardDistributor", distributorAddress);

  const totalGreenEvents = await distributor.totalGreenEvents();
  console.log(`🌱 Total Green Events Recorded: ${totalGreenEvents.toString()}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
