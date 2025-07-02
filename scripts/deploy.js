const { ethers } = require("hardhat");

async function main() {
  const initialSupply = ethers.parseEther(process.env.INITIAL_TOKEN_SUPPLY);

  const Token = await ethers.getContractFactory("Silvanus");
  const token = await Token.deploy(initialSupply);

  // Wait for deployment to complete
  await token.waitForDeployment();

  console.log("Silvanus deployed to:", await token.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
