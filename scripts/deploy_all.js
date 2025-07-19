const hre = require("hardhat");
const fs = require("fs");
const { ethers, upgrades } = hre;

async function main() {
  console.log("🚀 Starting comprehensive Silvanus deployment...\n");

  const [deployer] = await ethers.getSigners();
  const network = await ethers.provider.getNetwork();
  const balance = await ethers.provider.getBalance(deployer.address);

  console.log(`📡 Deploying to network: ${network.name} (Chain ID: ${network.chainId})`);
  console.log(`👤 Deployer address: ${deployer.address}`);
  console.log(`💰 Deployer balance: ${ethers.formatEther(balance)} ETH\n`);

  const grantBeneficiary = process.env.GRANT_BENEFICIARY;
  if (!grantBeneficiary) {
    console.error("❌ GRANT_BENEFICIARY is not defined in .env. Aborting.");
    process.exit(1);
  }

  const wallets = {
    developerTreasury: process.env.DEVELOPER_TREASURY,
    marketing: process.env.PROJECT_SUPPORT_AND_MARKETING,
    partnerships: process.env.PARTNERSHIPS,
    liquidityPool: process.env.LIQUIDITY_POOL,
    timelockBeneficiary: grantBeneficiary,
  };

  console.log("📋 Wallet addresses loaded:");
  for (const [label, address] of Object.entries(wallets)) {
    console.log(`   ${label.replace(/([A-Z])/g, " $1")}: ${address}`);
  }

  // Step 1: Deploy Silvanus Token
  console.log("\n🪙 Step 1: Deploying Silvanus Token...");
  const Silvanus = await ethers.getContractFactory("Silvanus");
  const silvanus = await upgrades.deployProxy(Silvanus, [ethers.parseEther("100000000")], {
    initializer: "initialize",
    kind: "uups",
  });
  await silvanus.waitForDeployment();

  const silvanusAddress = await silvanus.getAddress();
  const logicAddress = await upgrades.erc1967.getImplementationAddress(silvanusAddress);
  const totalSupply = await silvanus.totalSupply();

  console.log(`✅ Silvanus Token deployed to: ${silvanusAddress}`);
  console.log(`   Logic contract at: ${logicAddress}`);
  console.log(`   Initial supply minted to deployer: ${ethers.formatUnits(totalSupply, 18)} SVN`);

  // Step 2: Deploy TokenTimelock (used as Grant Wallet)
  console.log("\n🔒 Step 2: Deploying TokenTimelock...");
  const TokenTimelock = await ethers.getContractFactory("TokenTimelock");
  const releaseTime = Math.floor(Date.now() / 1000) + 60 * 60 * 24 * 90; // 90 days
  const timelock = await TokenTimelock.deploy(silvanusAddress, wallets.timelockBeneficiary, releaseTime);
  await timelock.waitForDeployment();
  const timelockAddress = await timelock.getAddress();

  console.log(`✅ TokenTimelock deployed to: ${timelockAddress}`);
  console.log(`   Beneficiary: ${wallets.timelockBeneficiary}`);
  console.log(`   Release date: ${new Date(releaseTime * 1000).toISOString()}`);

  console.log("\n⚙️  Step 3: Setting TokenTimelock as grantWallet...");
  await silvanus.setGrantWallet(timelockAddress);
  console.log(`✅ Grant wallet set to: ${timelockAddress}`);

  // Step 4: Deploy GreenRewardDistributor (proxy)
  console.log("\n🌿 Step 4: Deploying GreenRewardDistributor (UUPS Proxy)...");
  const baseReward = ethers.parseEther("1");
  const GreenRewardDistributor = await ethers.getContractFactory("GreenRewardDistributor");
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
  console.log(`✅ GreenRewardDistributor (proxy) deployed to: ${distributorAddress}`);

  // Step 5: Distribute initial allocations (except grant)
  console.log("\n💸 Step 5: Distributing initial token allocations...");
  const allocations = {
    [wallets.developerTreasury]: 12_500_000,
    [wallets.marketing]: 10_000_000,
    [wallets.partnerships]: 7_500_000,
    [wallets.liquidityPool]: 9_000_000,
    [distributorAddress]: 40_000_000,
  };

  for (const [address, amount] of Object.entries(allocations)) {
    const tokens = ethers.parseUnits(amount.toString(), 18);
    const tx = await silvanus.transfer(address, tokens);
    await tx.wait();
    console.log(`   ✅ Sent ${amount.toLocaleString()} SVN to ${address}`);
  }

  // Step 6: Deploy SVNPresale contract and fund it
  console.log("\n🛒 Step 6: Deploying SVNPresale contract...");
  const SVNPresale = await ethers.getContractFactory("SVNPresale");
  const presale = await SVNPresale.deploy(silvanusAddress);
  await presale.waitForDeployment();
  const presaleAddress = await presale.getAddress();
  console.log(`✅ SVNPresale deployed to: ${presaleAddress}`);

  const presaleAmount = ethers.parseUnits("21000000", 18);
  const presaleTx = await silvanus.transfer(presaleAddress, presaleAmount);
  await presaleTx.wait();
  console.log("   ✅ Transferred 21M SVN to Presale");

  const presaleBalance = await silvanus.balanceOf(presaleAddress);
  console.log(`   Presale contract balance: ${ethers.formatEther(presaleBalance)} SVN`);

  // Step 7: Verifications
  console.log("\n🔍 Step 7: Verifying contracts on Etherscan...");
  try {
    await hre.run("verify:verify", {
      address: logicAddress,
      constructorArguments: [],
    });
    console.log(`✅ Silvanus logic contract verified: ${logicAddress}`);
  } catch (err) {
    console.warn(`⚠️  Logic contract verification failed: ${err.message}`);
  }

  try {
    await hre.run("verify:verify", {
      address: timelockAddress,
      constructorArguments: [silvanusAddress, wallets.timelockBeneficiary, releaseTime],
    });
    console.log(`✅ TokenTimelock verified: ${timelockAddress}`);
  } catch (err) {
    console.warn(`⚠️  Timelock verification failed: ${err.message}`);
  }

  try {
    const distImpl = await upgrades.erc1967.getImplementationAddress(distributorAddress);
    await hre.run("verify:verify", {
      address: distImpl,
      constructorArguments: [],
    });
    console.log(`✅ GreenRewardDistributor logic verified: ${distImpl}`);
  } catch (err) {
    console.warn(`⚠️  Distributor verification failed: ${err.message}`);
  }

  try {
    await hre.run("verify:verify", {
      address: presaleAddress,
      constructorArguments: [silvanusAddress],
    });
    console.log(`✅ SVNPresale contract verified: ${presaleAddress}`);
  } catch (err) {
    console.warn(`⚠️  SVNPresale verification failed: ${err.message}`);
  }

  console.log("\n✅ DEPLOYMENT COMPLETE!");
}

main().catch((error) => {
  console.error("❌ DEPLOYMENT FAILED!");
  console.error(error);
  process.exit(1);
});
