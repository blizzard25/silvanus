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

  let silvanus, silvanusAddress, silvanusImpl;
  let timelock, timelockAddress;
  let distributor, distributorAddress, distributorImpl;
  let presale, presaleAddress;

  // Step 1: Deploy Silvanus Token with initialSupply
  try {
    console.log("\n🪙 Deploying Silvanus Token...");
    const Silvanus = await ethers.getContractFactory("Silvanus");
    silvanus = await upgrades.deployProxy(Silvanus, [ethers.parseEther("100000000")], {
      initializer: "initialize",
      kind: "uups",
    });
    await silvanus.waitForDeployment();
    silvanusAddress = await silvanus.getAddress();
    silvanusImpl = await upgrades.erc1967.getImplementationAddress(silvanusAddress);
    console.log(`✅ Silvanus deployed at: ${silvanusAddress}`);
    console.log(`   Logic implementation: ${silvanusImpl}`);
  } catch (error) {
    console.error("❌ Failed to deploy Silvanus Token:");
    console.error(error.message);
    throw error; // Fatal error - cannot continue without main token
  }

  // Step 2: Deploy TokenTimelock
  try {
    console.log("\n🔒 Deploying TokenTimelock...");
    const TokenTimelock = await ethers.getContractFactory("TokenTimelock");
    const releaseTime = Math.floor(Date.now() / 1000) + 60 * 60 * 24 * 90;
    timelock = await TokenTimelock.deploy(silvanusAddress, wallets.timelockBeneficiary, releaseTime);
    await timelock.waitForDeployment();
    timelockAddress = await timelock.getAddress();
    console.log(`✅ TokenTimelock deployed at: ${timelockAddress}`);
  } catch (error) {
    console.error("❌ Failed to deploy TokenTimelock:");
    console.error(error.message);
    console.log("⚠️  Continuing deployment without timelock...");
  }

  // Step 3: Set Grant Wallet (only if timelock deployed successfully)
  if (timelockAddress) {
    try {
      console.log("\n⚙️ Setting grant wallet...");
      await silvanus.setGrantWallet(timelockAddress);
      console.log(`✅ Grant wallet set to: ${timelockAddress}`);
    } catch (error) {
      console.error("❌ Failed to set grant wallet:");
      console.error(error.message);
      console.log("⚠️  Continuing deployment...");
    }
  }

  // Step 4: Deploy GreenRewardDistributor
  try {
    console.log("\n🌿 Deploying GreenRewardDistributor...");
    const GreenRewardDistributor = await ethers.getContractFactory("GreenRewardDistributor");
    const baseReward = ethers.parseEther("1");
    distributor = await upgrades.deployProxy(
      GreenRewardDistributor,
      [silvanusAddress, baseReward],
      {
        initializer: "initialize",
        kind: "uups",
      }
    );
    await distributor.waitForDeployment();
    distributorAddress = await distributor.getAddress();
    distributorImpl = await upgrades.erc1967.getImplementationAddress(distributorAddress);
    console.log(`✅ Distributor deployed at: ${distributorAddress}`);
    console.log(`   Logic implementation: ${distributorImpl}`);
  } catch (error) {
    console.error("❌ Failed to deploy GreenRewardDistributor:");
    console.error(error.message);
    console.log("⚠️  Continuing deployment without distributor...");
  }

  // Step 5: Distribute allocations
  try {
    console.log("\n💸 Distributing allocations...");
    const allocations = {
      [wallets.developerTreasury]: 12_500_000,
      [wallets.marketing]: 10_000_000,
      [wallets.partnerships]: 7_500_000,
      [wallets.liquidityPool]: 9_000_000,
    };

    if (distributorAddress) {
      allocations[distributorAddress] = 40_000_000;
    }

    for (const [addr, amount] of Object.entries(allocations)) {
      try {
        const tokens = ethers.parseUnits(amount.toString(), 18);
        const tx = await silvanus.transfer(addr, tokens);
        await tx.wait();
        console.log(`✅ Transferred ${amount.toLocaleString()} SVN to ${addr}`);
      } catch (error) {
        console.error(`❌ Failed to transfer ${amount.toLocaleString()} SVN to ${addr}:`);
        console.error(error.message);
        console.log("⚠️  Continuing with remaining transfers...");
      }
    }
  } catch (error) {
    console.error("❌ Failed during token distribution:");
    console.error(error.message);
    console.log("⚠️  Continuing deployment...");
  }

  // Step 6: Deploy Presale
  try {
    console.log("\n🛒 Deploying SVNPresale...");
    const SVNPresale = await ethers.getContractFactory("SVNPresale");
    presale = await SVNPresale.deploy(silvanusAddress);
    await presale.waitForDeployment();
    presaleAddress = await presale.getAddress();
    console.log(`✅ SVNPresale deployed at: ${presaleAddress}`);

    const presaleAmount = ethers.parseUnits("21000000", 18);
    const txPresale = await silvanus.transfer(presaleAddress, presaleAmount);
    await txPresale.wait();
    console.log("✅ Transferred 21M SVN to Presale");
  } catch (error) {
    console.error("❌ Failed to deploy or fund SVNPresale:");
    console.error(error.message);
    console.log("⚠️  Continuing to verification...");
  }

  // Step 7: Verify contracts
  console.log("\n🔍 Verifying on Etherscan...");
  const verify = async (address, args, name) => {
    try {
      await hre.run("verify:verify", { address, constructorArguments: args });
      console.log(`✅ Verified ${name}: ${address}`);
    } catch (e) {
      console.warn(`⚠️  Verification failed for ${name} (${address}): ${e.message}`);
    }
  };

  if (silvanusImpl) await verify(silvanusImpl, [], "Silvanus Logic");
  if (timelockAddress) await verify(timelockAddress, [silvanusAddress, wallets.timelockBeneficiary, Math.floor(Date.now() / 1000) + 60 * 60 * 24 * 90], "TokenTimelock");
  if (distributorImpl) await verify(distributorImpl, [], "Distributor Logic");
  if (presaleAddress) await verify(presaleAddress, [silvanusAddress], "SVNPresale");

  console.log("\n🎉 Deployment complete!");
  console.log("\n📋 Deployment Summary:");
  console.log(`   Silvanus Token: ${silvanusAddress || "❌ Failed"}`);
  console.log(`   TokenTimelock: ${timelockAddress || "❌ Failed"}`);
  console.log(`   GreenRewardDistributor: ${distributorAddress || "❌ Failed"}`);
  console.log(`   SVNPresale: ${presaleAddress || "❌ Failed"}`);
}

main().catch((err) => {
  console.error("❌ DEPLOYMENT FAILED!");
  console.error(err);
  process.exit(1);
});
