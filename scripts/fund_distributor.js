const { ethers } = require("hardhat");

async function main() {
  const tokenAddress = "0x3fcE4d2E8bfF26732EAAf942B67bF31a1e5a965d";
  const distributorAddress = "0x1F13bdF1B093ECEDc6A8731423083FB24e87DACb";

  const [deployer] = await ethers.getSigners();
  const token = await ethers.getContractAt("Silvanus", tokenAddress);
  
  const tx = await token.transfer(distributorAddress, ethers.parseEther("1000"));

  await tx.wait();

  console.log(`✅ Sent tokens to distributor: ${distributorAddress}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
