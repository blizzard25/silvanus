const hre = require("hardhat");

async function main() {
  console.log("hre.ethers:", typeof hre.ethers);
  console.log("hre.ethers.utils:", typeof hre.ethers?.utils);
  console.log("hre.ethers.utils.parseEther:", typeof hre.ethers?.utils?.parseEther);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
