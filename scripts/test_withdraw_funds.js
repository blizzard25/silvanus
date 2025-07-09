const { ethers } = require("ethers"); // Standalone ethers v6
const hre = require("hardhat");
require("dotenv").config();

const PRESALE_ADDRESS = process.env.PRESALE_CONTRACT;

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Using wallet:", deployer.address);

  const presale = await hre.ethers.getContractAt("SVNPresale", PRESALE_ADDRESS);

  const owner = await presale.owner();
  if (owner !== deployer.address) {
    throw new Error("❌ You are not the owner of the contract. Aborting.");
  }
  console.log("✅ Owner verified.");

  const balance = await hre.ethers.provider.getBalance(PRESALE_ADDRESS);
  console.log(`📦 Contract ETH balance: ${ethers.formatEther(balance)} ETH`);

  if (balance === 0n) {
    console.log("⚠️ Contract balance is zero. Nothing to withdraw.");
    return;
  }

  console.log("⏳ Withdrawing funds...");
  const tx = await presale.withdrawETH();
  await tx.wait();

  console.log("✅ Funds successfully withdrawn to:", deployer.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
