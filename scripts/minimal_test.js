const { ethers, upgrades } = require("hardhat");

async function main() {
  console.log("Testing minimal deployment...");
  
  const initialSupply = ethers.parseEther("100000000");
  const Silvanus = await ethers.getContractFactory("Silvanus");
  
  console.log("About to deploy proxy...");
  const proxy = await upgrades.deployProxy(Silvanus, [initialSupply], {
    initializer: "initialize",
    kind: "uups"
  });
  
  console.log("Waiting for deployment...");
  await proxy.waitForDeployment();
  
  console.log("Getting address...");
  const address = await proxy.getAddress();
  console.log("Deployed to:", address);
}

main().catch((error) => {
  console.error("Error:", error);
  process.exitCode = 1;
});
