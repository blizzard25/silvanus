const { ethers, upgrades } = require("hardhat");

async function main() {
  const initialSupply = ethers.parseEther("100000000");

  const Silvanus = await ethers.getContractFactory("Silvanus");
  const proxy = await upgrades.deployProxy(Silvanus, [initialSupply], {
    initializer: "initialize",
    kind: "uups",
    timeout: 120000, // 2 minutes
    pollingInterval: 3000 // 3 seconds
  });

  await proxy.waitForDeployment();
  console.log("Silvanus (proxy) deployed to:", await proxy.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
