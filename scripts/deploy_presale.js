const { ethers } = require("hardhat");

async function main() {
  const tokenAddress = process.env.TOKEN_ADDRESS;
  if (!tokenAddress) {
    throw new Error("Missing TOKEN_ADDRESS in .env");
  }

  const SVNPresale = await ethers.getContractFactory("SVNPresale");
  const presale = await SVNPresale.deploy(tokenAddress);
  await presale.waitForDeployment();

  const presaleAddress = await presale.getAddress();
  console.log("SVNPresale deployed to:", presaleAddress);

  const [signer] = await ethers.getSigners();
  const Silvanus = await ethers.getContractAt("Silvanus", tokenAddress, signer);
  const amount = ethers.parseEther("21000000");

  const tx = await Silvanus.transfer(presaleAddress, amount);
  await tx.wait();
  console.log("Transferred 21M SVN to Presale");

  const balance = await Silvanus.balanceOf(presaleAddress);
  console.log(`Presale contract balance: ${ethers.formatEther(balance)} SVN`);
}

main().catch((error) => {
  console.error("Deployment failed:", error);
  process.exitCode = 1;
});
