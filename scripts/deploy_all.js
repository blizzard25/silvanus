const hre = require("hardhat");
const fs = require("fs");

async function main() {
  const ethers = hre.ethers;
  const run = hre.run;
  const formatEther = ethers.formatEther;

  console.log("🚀 Starting comprehensive Silvanus deployment...\n");

  const [deployer] = await ethers.getSigners();
  const network = await ethers.provider.getNetwork();
  const balance = await ethers.provider.getBalance(deployer.address);

  console.log(`📡 Deploying to network: ${network.name} (Chain ID: ${network.chainId})`);
  console.log(`👤 Deployer address: ${deployer.address}`);
  console.log(`💰 Deployer balance: ${formatEther(balance)} ETH\n`);

  const wallets = {
    developerTreasury: process.env.DEVELOPER_TREASURY,
    marketing: process.env.PROJECT_SUPPORT_AND_MARKETING,
    partnerships: process.env.PARTNERSHIPS,
    liquidityPool: process.env.LIQUIDITY_POOL,
    timelockBeneficiary: process.env.TIMELOCK_BENEFICIARY,
  };

  console.log(`📋 Wallet addresses loaded:`);
  for (const [label, address] of Object.entries(wallets)) {
    console.log(`   ${label.replace(/([A-Z])/g, ' $1')}: ${address}`);
  }

  // Step 1: Deploy Silvanus Token Proxy
  console.log("\n🪙 Step 1: Deploying Silvanus Token...");
  const Silvanus = await ethers.getContractFactory("Silvanus");
  const silvanus = await upgrades.deployProxy(Silvanus, [deployer.address], {
    initializer: "initialize",
    kind: "uups",
  });
  await silvanus.waitForDeployment();

  const silvanusAddress = await silvanus.getAddress();
  const logicAddress = await upgrades.erc1967.getImplementationAddress(silvanusAddress);

  console.log(`✅ Silvanus Token deployed to: ${silvanusAddress}`);
  console.log(`   Logic contract at: ${logicAddress}`);

  const totalSupply = await silvanus.totalSupply();
  console.log(`   Initial supply minted to deployer: ${formatEther(totalSupply)} SVN`);

  // Step 2: Deploy TokenTimelock
  console.log("\n🔒 Step 2: Deploying TokenTimelock...");
  const TokenTimelock = await ethers.getContractFactory("TokenTimelock");
  const releaseTime = Math.floor(Date.now() / 1000) + 60 * 60 * 24 * 90; // 90 days
  const timelock = await TokenTimelock.deploy(silvanusAddress, wallets.timelockBeneficiary, releaseTime);
  await timelock.waitForDeployment();
  const timelockAddress = await timelock.getAddress();

  console.log(`✅ TokenTimelock deployed to: ${timelockAddress}`);
  console.log(`   Beneficiary: ${wallets.timelockBeneficiary}`);
  console.log(`   Release date: ${new Date(releaseTime * 1000).toISOString()}`);

  // Step 3: Set TokenTimelock as grant wallet
  console.log("\n⚙️  Step 3: Setting TokenTimelock as grantWallet...");
  const currentOwner = await silvanus.owner();
  if (currentOwner.toLowerCase() !== deployer.address.toLowerCase()) {
    console.error("❌ Deployer is not owner or pending owner");
    throw new Error("Deployer is not owner or pending owner");
  }

  try {
    await silvanus.setGrantWallet(timelockAddress);
    console.log(`✅ Grant wallet set to: ${timelockAddress}`);
  } catch (err) {
    console.error("❌ Failed to set grant wallet:", err.message);
    throw err;
  }

  // Step 4: Transfer funds to wallets
  console.log("\n💸 Step 4: Distributing initial token allocations...");
  const allocations = {
    [wallets.developerTreasury]: 12_500_000,
    [wallets.marketing]: 10_000_000,
    [wallets.partnerships]: 7_500_000,
    [wallets.liquidityPool]: 9_000_000,
    [timelockAddress]: 7_500_000, // Grants via timelock
  };

  for (const [address, amount] of Object.entries(allocations)) {
    const tokens = ethers.parseUnits(amount.toString(), 18);
    const tx = await silvanus.transfer(address, tokens);
    await tx.wait();
    console.log(`   ✅ Sent ${amount.toLocaleString()} SVN to ${address}`);
  }

  // Step 5: Verify contracts
  console.log("\n🔍 Step 5: Verifying contracts on Etherscan...");
  try {
    await run("verify:verify", {
      address: logicAddress,
      constructorArguments: [],
    });
    console.log(`✅ Silvanus logic contract verified: ${logicAddress}`);
  } catch (err) {
    console.warn(`⚠️  Logic contract verification failed: ${err.message}`);
  }

  try {
    await run("verify:verify", {
      address: timelockAddress,
      constructorArguments: [silvanusAddress, wallets.timelockBeneficiary, releaseTime],
    });
    console.log(`✅ TokenTimelock verified: ${timelockAddress}`);
  } catch (err) {
    console.warn(`⚠️  Timelock verification failed: ${err.message}`);
  }

  console.log("\n✅ DEPLOYMENT COMPLETE!");
}

main().catch((error) => {
  console.error("❌ DEPLOYMENT FAILED!");
  console.error(error);
  process.exit(1);
});
