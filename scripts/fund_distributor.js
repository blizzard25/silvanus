const { ethers } = require("hardhat");

async function main() {
  const tokenAddress = process.env.TOKEN_ADDRESS;
  const distributorAddress = process.env.REWARD_CONTRACT;

  const [deployer] = await ethers.getSigners();
  const token = await ethers.getContractAt("Silvanus", tokenAddress);
  
  const tx = await token.transfer(distributorAddress, ethers.parseEther("4000000"));

  await tx.wait();

  console.log(`Sent tokens to distributor: ${distributorAddress}`);
  const newBalance = await token.balanceOf(distributorAddress);
  console.log(`Distributor now holds: ${ethers.formatEther(newBalance)} SVN`);

}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
