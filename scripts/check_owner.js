const { ethers } = require("hardhat");
require("dotenv").config();

const PRESALE_ADDRESS = process.env.PRESALE_CONTRACT;

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Using wallet:", deployer.address);

  const Presale = await ethers.getContractFactory("SVNPresale");
  const presale = await Presale.attach(PRESALE_ADDRESS);

  const owner = await presale.owner();
  console.log("Presale contract owner:", owner);

  if (owner === deployer.address) {
    console.log("✅ You are the owner of the presale contract.");
  } else {
    console.log("⚠️ You are NOT the owner of the presale contract.");
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
