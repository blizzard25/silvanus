const { ethers } = require("hardhat");

async function main() {
  console.log("🔍 Checking contract bytecode...\n");

  const silvanusAddress = "0x8D61D39a7347AfcBba983934A15b435a2B602DC2";
  const timelockAddress = "0xa49650F29e79e5ab8fDDc2abE2Eb3C3D2375ce40";

  console.log(`Checking Silvanus proxy at: ${silvanusAddress}`);
  const silvanusCode = await ethers.provider.getCode(silvanusAddress);
  console.log(`Silvanus code length: ${silvanusCode.length} characters`);
  console.log(`Has bytecode: ${silvanusCode.length > 10 ? '✅ YES' : '❌ NO'}`);

  console.log(`\nChecking TokenTimelock at: ${timelockAddress}`);
  const timelockCode = await ethers.provider.getCode(timelockAddress);
  console.log(`TokenTimelock code length: ${timelockCode.length} characters`);
  console.log(`Has bytecode: ${timelockCode.length > 10 ? '✅ YES' : '❌ NO'}`);

  if (silvanusCode.length > 10) {
    console.log("\n🧪 Testing Silvanus proxy function calls...");
    try {
      const Silvanus = await ethers.getContractFactory("Silvanus");
      const silvanusContract = Silvanus.attach(silvanusAddress);
      
      const totalSupply = await silvanusContract.totalSupply();
      console.log(`✅ totalSupply: ${ethers.formatEther(totalSupply)} SVN`);
      
      const owner = await silvanusContract.owner();
      console.log(`✅ owner: ${owner}`);
      
    } catch (error) {
      console.log(`❌ Function call failed: ${error.message}`);
    }
  }
}

main().catch((error) => {
  console.error("Check failed:", error);
  process.exitCode = 1;
});
