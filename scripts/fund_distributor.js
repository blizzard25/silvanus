const { ethers } = require("hardhat");

async function main() {
  const tokenAddress = "0x3fcE4d2E8bfF26732EAAf942B67bF31a1e5a965d";
  const distributorAddress = "0xa2DF2C83AE5DEd5992cF98486f0ce65504C5523C";

  const [deployer] = await ethers.getSigners();
  const token = await ethers.getContractAt("Silvanus", tokenAddress);
  
  const tx = await token.transfer(distributorAddress, ethers.parseEther("1000000"));

  await tx.wait();

  console.log(`✅ Sent tokens to distributor: ${distributorAddress}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
