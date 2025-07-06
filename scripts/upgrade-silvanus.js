const { ethers, upgrades } = require("hardhat");

async function main() {
  const proxyAddress = process.env.PROXY_ADDRESS; // e.g., 0xabc123...
  const SilvanusV2 = await ethers.getContractFactory("SilvanusV2");

  const upgraded = await upgrades.upgradeProxy(proxyAddress, SilvanusV2);

  console.log("Silvanus upgraded at:", await upgraded.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
