// deploy_all.js
const hre = require("hardhat");
const fs = require("fs");
const { ethers, upgrades } = hre;

async function main() {
  console.log("🚀 Starting comprehensive Silvanus deployment...\n");

  const [deployer] = await ethers.getSigners();
  const network = await ethers.provider.getNetwork();
  const balance = await ethers.provider.getBalance(deployer.address);

  console.log(`📡 Network: ${network.name} (Chain ID: ${network.chainId})`);
  console.log(`👤 Deployer: ${deployer.address}`);
  console.log(`💰 Balance: ${ethers.formatEther(balance)} ETH\n`);

  const grantBeneficiary = process.env.GRANT_BENEFICIARY;
  if (!grantBeneficiary) throw new Error("❌ GRANT_BENEFICIARY missing in .env");

  const walletsRaw = {
    developerTreasury: process.env.DEVELOPER_TREASURY,
    marketing: process.env.PROJECT_SUPPORT_AND_MARKETING,
    partnerships: process.env.PARTNERSHIPS,
    liquidityPool: process.env.LIQUIDITY_POOL,
    timelockBeneficiary: grantBeneficiary,
  };

  const wallets = {};
  for (const [key, addr] of Object.entries(walletsRaw)) {
    if (!addr?.trim()) throw new Error(`❌ Missing address for ${key}`);
    wallets[key] = ethers.getAddress(addr.trim());
    console.log(`✅ ${key}: ${wallets[key]}`);
  }

  // Step 1: Deploy Silvanus Token with initialSupply
  console.log("\n🪙 Deploying Silvanus Token...");
  const Silvanus = await ethers.getContractFactory("Silvanus");
  const initialSupply = ethers.parseUnits("100000000", 18);
  const silvanus = await upgrades.deployProxy(Silvanus, [initialSupply], {
    initializer: "initialize",
    kind: "uups",
  });
  await silvanus.waitForDeployment();
  const silvanusAddress = await silvanus.getAddress();
  const silvanusImpl = await upgrades.erc1967.getImplementationAddress(silvanusAddress);
  console.log(`✅ Silvanus deployed at: ${silvanusAddress}`);
  console.log(`   Logic implementation: ${silvanusImpl}`);

  // Step 2: Deploy TokenTimelock
  console.log("\n🔒 Deploying TokenTimelock...");
  const TokenTimelock = await ethers.getContractFactory("TokenTimelock");
  const releaseTime = Math.floor(Date.now() / 1000) + 60 * 60 * 24 * 90;
  const timelock = await TokenTimelock.deploy(silvanusAddress, wallets.timelockBeneficiary, releaseTime);
  await timelock.waitForDeployment();
  const timelockAddress = await timelock.getAddress();
  console.log(`✅ TokenTimelock deployed at: ${timelockAddress}`);

  // Step 3: Set Grant Wallet
  console.log("\n⚙️ Setting grant wallet...");
  await silvanus.setGrantWallet(timelockAddress);
  console.log(`✅ Grant wallet set to: ${timelockAddress}`);

  // Step 4: Deploy GreenRewardDistributor
  console.log("\n🌿 Deploying GreenRewardDistributor...");
  const GreenRewardDistributor = await ethers.getContractFactory("GreenRewardDistributor");
  const baseReward = ethers.parseEther("1");
  const distributor = await upgrades.deployProxy(
    GreenRewardDistributor,
    [silvanusAddress, baseReward],
    {
      initializer: "initialize",
      kind: "uups",
    }
  );
  await distributor.waitForDeployment();
  const distributorAddress = await distributor.getAddress();
  const distributorImpl = await upgrades.erc1967.getImplementationAddress(distributorAddress);
  console.log(`✅ Distributor deployed at: ${distributorAddress}`);
  console.log(`   Logic implementation: ${distributorImpl}`);

  // Step 5: Distribute allocations
  console.log("\n💸 Distributing allocations...");
  const allocations = {
    [wallets.developerTreasury]: 12_500_000,
    [wallets.marketing]: 10_000_000,
    [wallets.partnerships]: 7_500_000,
    [wallets.liquidityPool]: 9_000_000,
    [distributorAddress]: 40_000_000,
  };

  for (const [addr, amount] of Object.entries(allocations)) {
    const tokens = ethers.parseUnits(amount.toString(), 18);
    const tx = await silvanus.transfer(addr, tokens);
    await tx.wait();
    console.log(`✅ Transferred ${amount.toLocaleString()} SVN to ${addr}`);
  }

  // Step 6: Deploy Presale
  console.log("\n🛒 Deploying SVNPresale...");
  const SVNPresale = await ethers.getContractFactory("SVNPresale");
  const presale = await SVNPresale.deploy(silvanusAddress);
  await presale.waitForDeployment();
  const presaleAddress = await presale.getAddress();
  console.log(`✅ SVNPresale deployed at: ${presaleAddress}`);

  const presaleAmount = ethers.parseUnits("21000000", 18);
  const txPresale = await silvanus.transfer(presaleAddress, presaleAmount);
  await txPresale.wait();
  console.log("✅ Transferred 21M SVN to Presale");

  // Step 7: Verify contracts
  console.log("\n🔍 Verifying on Etherscan...");
  const verify = async (address, args) => {
    try {
      await hre.run("verify:verify", { address, constructorArguments: args });
      console.log(`✅ Verified: ${address}`);
    } catch (e) {
      console.warn(`⚠️  Verification failed for ${address}: ${e.message}`);
    }
  };

  await verify(silvanusImpl, []);
  await verify(timelockAddress, [silvanusAddress, wallets.timelockBeneficiary, releaseTime]);
  await verify(distributorImpl, []);
  await verify(presaleAddress, [silvanusAddress]);

  console.log("\n🎉 Deployment complete!");
}

main().catch((err) => {
  console.error("❌ DEPLOYMENT FAILED!");
  console.error(err);
  process.exit(1);
});
