const { ethers } = require("ethers");
const hre = require("hardhat");

async function main() {
  const contractAddress = "0x3E80B5768D2a48Da2f5C235f6a0d601a769A9Ca7";
  const [deployer] = await hre.ethers.getSigners();

  const recipient = "0x0B5059636CeC2Fc2148a78e2E93bF135eDfb02Ad";
  console.log("Sender:", deployer.address);
  console.log("Recipient:", recipient);

  const token = await hre.ethers.getContractAt("SilvanusToken", contractAddress);

  const amount = ethers.parseEther("10"); // ← notice: now from raw ethers, not hre.ethers
  const tx = await token.transfer(recipient, amount);
  await tx.wait();

  console.log(`Transferred 10 SVN to ${recipient}`);

  const senderBalance = await token.balanceOf(deployer.address);
  const recipientBalance = await token.balanceOf(recipient);

  console.log(`Sender balance: ${ethers.formatEther(senderBalance)} SVN`);
  console.log(`Recipient balance: ${ethers.formatEther(recipientBalance)} SVN`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
