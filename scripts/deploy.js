const { ethers, upgrades } = require("hardhat");

async function main() {
  const initialSupply = ethers.parseEther("100000000");

  const Silvanus = await ethers.getContractFactory("Silvanus");
  const proxy = await upgrades.deployProxy(Silvanus, [initialSupply], {
    initializer: "initialize",
    kind: "uups"
  });

  await proxy.waitForDeployment();
  console.log("Silvanus (proxy) deployed to:", await proxy.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
