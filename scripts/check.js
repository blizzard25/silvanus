const { ethers } = require("hardhat");


async function main() {
  const contractAddress = "0x3E80B5768D2a48Da2f5C235f6a0d601a769A9Ca7";
  const SilvanusToken = await hre.ethers.getContractAt("SilvanusToken", contractAddress);

  const name = await SilvanusToken.name();
  const symbol = await SilvanusToken.symbol();
  const totalSupply = await SilvanusToken.totalSupply();

  console.log(`Name: ${name}`);
  console.log(`Symbol: ${symbol}`);
  console.log(`Total Supply (raw): ${totalSupply.toString()}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
