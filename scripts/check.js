const { ethers } = require("hardhat");

async function main() {
  const tokenAddress = process.env.TOKEN_ADDRESS;
  const [deployer] = await ethers.getSigners();

  const token = await ethers.getContractAt("Silvanus", tokenAddress);
  const balance = await token.balanceOf(deployer.address);

  console.log(`Balance of ${deployer.address}: ${ethers.formatEther(balance)} tokens`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

