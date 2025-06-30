const { ethers } = require("hardhat");

async function main() {
  const silvanusTokenAddress = "0x8f4FB6498A4D90FBc19c5b0b15F43869D7818Caa";
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
