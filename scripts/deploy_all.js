const { ethers, upgrades } = require("hardhat");
require("dotenv").config();

async function main() {
  console.log("🚀 Starting comprehensive Silvanus deployment...\n");

  const network = await ethers.provider.getNetwork();
  console.log(`📡 Deploying to network: ${network.name} (Chain ID: ${network.chainId})`);

  const [deployer] = await ethers.getSigners();
  const deployerAddress = await deployer.getAddress();
  console.log(`👤 Deployer address: ${deployerAddress}`);
  console.log(`💰 Deployer balance: ${ethers.formatEther(await ethers.provider.getBalance(deployerAddress))} ETH\n`);

  const {
    DEVELOPER_TREASURY,
    PROJECT_SUPPORT_AND_MARKETING,
    PARTNERSHIPS,
    LIQUIDITY_POOL,
    TIMELOCK_BENEFICIARY
  } = process.env;

  const requiredAddresses = {
    DEVELOPER_TREASURY,
    PROJECT_SUPPORT_AND_MARKETING,
    PARTNERSHIPS,
    LIQUIDITY_POOL,
    TIMELOCK_BENEFICIARY
  };

  for (const [name, address] of Object.entries(requiredAddresses)) {
    if (!address) {
      throw new Error(`❌ Missing required environment variable: ${name}`);
    }
    if (!ethers.isAddress(address)) {
      throw new Error(`❌ Invalid address for ${name}: ${address}`);
    }
  }

  console.log("📋 Wallet addresses loaded:");
  console.log(`   Developer Treasury: ${DEVELOPER_TREASURY}`);
  console.log(`   Project Support & Marketing: ${PROJECT_SUPPORT_AND_MARKETING}`);
  console.log(`   Partnerships: ${PARTNERSHIPS}`);
  console.log(`   Liquidity Pool: ${LIQUIDITY_POOL}`);
  console.log(`   Timelock Beneficiary: ${TIMELOCK_BENEFICIARY}\n`);

  const TOTAL_SUPPLY = ethers.parseEther("100000000"); // 100M
  const PRESALE_ALLOCATION = ethers.parseEther("21000000"); // 21M
  const REWARDS_ALLOCATION = ethers.parseEther("40000000"); // 40M
  const DEV_TREASURY_ALLOCATION = ethers.parseEther("12500000"); // 12.5M
  const LIQUIDITY_ALLOCATION = ethers.parseEther("9000000"); // 9M
  const PARTNERSHIPS_ALLOCATION = ethers.parseEther("7500000"); // 7.5M
  const PROJECT_SUPPORT_ALLOCATION = ethers.parseEther("10000000"); // 10M

  console.log("💎 Token allocation plan:");
  console.log(`   Total Supply: ${ethers.formatEther(TOTAL_SUPPLY)} SVN`);
  console.log(`   Presale: ${ethers.formatEther(PRESALE_ALLOCATION)} SVN`);
  console.log(`   Rewards: ${ethers.formatEther(REWARDS_ALLOCATION)} SVN`);
  console.log(`   Dev Treasury: ${ethers.formatEther(DEV_TREASURY_ALLOCATION)} SVN`);
  console.log(`   Liquidity Pool: ${ethers.formatEther(LIQUIDITY_ALLOCATION)} SVN`);
  console.log(`   Partnerships: ${ethers.formatEther(PARTNERSHIPS_ALLOCATION)} SVN`);
  console.log(`   Project Support: ${ethers.formatEther(PROJECT_SUPPORT_ALLOCATION)} SVN\n`);

  const deploymentResults = {};

  try {
    console.log("🪙 Step 1: Deploying Silvanus Token...");
    
    const Silvanus = await ethers.getContractFactory("Silvanus");
    const silvanusProxy = await upgrades.deployProxy(Silvanus, [TOTAL_SUPPLY], {
      initializer: "initialize"
    });
    
    await silvanusProxy.waitForDeployment();
    const silvanusAddress = await silvanusProxy.getAddress();
    deploymentResults.silvanus = silvanusAddress;
    
    console.log(`✅ Silvanus Token deployed to: ${silvanusAddress}`);
    console.log(`   Initial supply minted to deployer: ${ethers.formatEther(TOTAL_SUPPLY)} SVN\n`);

    console.log("🔒 Step 2: Deploying TokenTimelock...");
    
    const currentTime = Math.floor(Date.now() / 1000);
    const releaseTime = currentTime + (90 * 24 * 60 * 60); // 90 days in seconds
    const releaseDate = new Date(releaseTime * 1000);
    
    console.log(`   Release time: ${releaseTime} (${releaseDate.toISOString()})`);
    
    const TokenTimelock = await ethers.getContractFactory("TokenTimelock");
    const timelock = await TokenTimelock.deploy(
      silvanusAddress,
      TIMELOCK_BENEFICIARY,
      releaseTime
    );
    
    await timelock.waitForDeployment();
    const timelockAddress = await timelock.getAddress();
    deploymentResults.timelock = timelockAddress;
    
    console.log(`✅ TokenTimelock deployed to: ${timelockAddress}`);
    console.log(`   Beneficiary: ${TIMELOCK_BENEFICIARY}`);
    console.log(`   Release date: ${releaseDate.toISOString()}\n`);

    console.log("⚙️  Step 3: Setting TokenTimelock as grantWallet...");
    
    const setGrantWalletTx = await silvanusProxy.setGrantWallet(timelockAddress);
    await setGrantWalletTx.wait();
    
    console.log(`✅ TokenTimelock set as grantWallet in Silvanus Token\n`);

    console.log("🌱 Step 4: Deploying GreenRewardDistributor...");
    
    const baseReward = ethers.parseEther("1"); // 1 SVN base reward
    const GreenRewardDistributor = await ethers.getContractFactory("GreenRewardDistributor");
    const distributorProxy = await upgrades.deployProxy(
      GreenRewardDistributor,
      [silvanusAddress, baseReward],
      { initializer: "initialize" }
    );
    
    await distributorProxy.waitForDeployment();
    const distributorAddress = await distributorProxy.getAddress();
    deploymentResults.distributor = distributorAddress;
    
    console.log(`✅ GreenRewardDistributor deployed to: ${distributorAddress}`);
    console.log(`   Base reward: ${ethers.formatEther(baseReward)} SVN\n`);

    console.log("💰 Step 5: Deploying SVNPresale...");
    
    const SVNPresale = await ethers.getContractFactory("SVNPresale");
    const presale = await SVNPresale.deploy(silvanusAddress);
    await presale.waitForDeployment();
    
    const presaleAddress = await presale.getAddress();
    deploymentResults.presale = presaleAddress;
    
    console.log(`✅ SVNPresale deployed to: ${presaleAddress}\n`);

    console.log("📤 Step 6: Distributing tokens...");
    
    console.log(`   Transferring ${ethers.formatEther(PRESALE_ALLOCATION)} SVN to Presale...`);
    const presaleTransferTx = await silvanusProxy.transfer(presaleAddress, PRESALE_ALLOCATION);
    await presaleTransferTx.wait();
    
    console.log(`   Transferring ${ethers.formatEther(REWARDS_ALLOCATION)} SVN to Rewards Distributor...`);
    const rewardsTransferTx = await silvanusProxy.transfer(distributorAddress, REWARDS_ALLOCATION);
    await rewardsTransferTx.wait();
    
    if (DEVELOPER_TREASURY.toLowerCase() !== deployerAddress.toLowerCase()) {
      console.log(`   Transferring ${ethers.formatEther(DEV_TREASURY_ALLOCATION)} SVN to Developer Treasury...`);
      const devTreasuryTx = await silvanusProxy.transfer(DEVELOPER_TREASURY, DEV_TREASURY_ALLOCATION);
      await devTreasuryTx.wait();
    } else {
      console.log(`   Developer Treasury is deployer - keeping ${ethers.formatEther(DEV_TREASURY_ALLOCATION)} SVN`);
    }
    
    console.log(`   Transferring ${ethers.formatEther(LIQUIDITY_ALLOCATION)} SVN to Liquidity Pool...`);
    const liquidityTx = await silvanusProxy.transfer(LIQUIDITY_POOL, LIQUIDITY_ALLOCATION);
    await liquidityTx.wait();
    
    console.log(`   Transferring ${ethers.formatEther(PARTNERSHIPS_ALLOCATION)} SVN to Partnerships...`);
    const partnershipsTx = await silvanusProxy.transfer(PARTNERSHIPS, PARTNERSHIPS_ALLOCATION);
    await partnershipsTx.wait();
    
    console.log(`   Transferring ${ethers.formatEther(PROJECT_SUPPORT_ALLOCATION)} SVN to Project Support & Marketing...`);
    const projectSupportTx = await silvanusProxy.transfer(PROJECT_SUPPORT_AND_MARKETING, PROJECT_SUPPORT_ALLOCATION);
    await projectSupportTx.wait();
    
    console.log("✅ Token distribution completed!\n");

    console.log("🔍 Step 7: Verifying token balances...");
    
    const balances = {
      presale: await silvanusProxy.balanceOf(presaleAddress),
      distributor: await silvanusProxy.balanceOf(distributorAddress),
      devTreasury: await silvanusProxy.balanceOf(DEVELOPER_TREASURY),
      liquidity: await silvanusProxy.balanceOf(LIQUIDITY_POOL),
      partnerships: await silvanusProxy.balanceOf(PARTNERSHIPS),
      projectSupport: await silvanusProxy.balanceOf(PROJECT_SUPPORT_AND_MARKETING),
      deployer: await silvanusProxy.balanceOf(deployerAddress)
    };
    
    console.log("   Final token balances:");
    console.log(`     Presale Contract: ${ethers.formatEther(balances.presale)} SVN`);
    console.log(`     Rewards Distributor: ${ethers.formatEther(balances.distributor)} SVN`);
    console.log(`     Developer Treasury: ${ethers.formatEther(balances.devTreasury)} SVN`);
    console.log(`     Liquidity Pool: ${ethers.formatEther(balances.liquidity)} SVN`);
    console.log(`     Partnerships: ${ethers.formatEther(balances.partnerships)} SVN`);
    console.log(`     Project Support: ${ethers.formatEther(balances.projectSupport)} SVN`);
    console.log(`     Deployer Remaining: ${ethers.formatEther(balances.deployer)} SVN\n`);
    
    const totalDistributed = balances.presale + balances.distributor + balances.devTreasury + 
                           balances.liquidity + balances.partnerships + balances.projectSupport + balances.deployer;
    
    console.log(`   Total distributed: ${ethers.formatEther(totalDistributed)} SVN`);
    console.log(`   Expected total: ${ethers.formatEther(TOTAL_SUPPLY)} SVN`);
    
    if (totalDistributed === TOTAL_SUPPLY) {
      console.log("✅ Token distribution verification passed!\n");
    } else {
      console.log("❌ Token distribution verification failed!\n");
    }

    console.log("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!");
    console.log("=" .repeat(60));
    console.log("📋 CONTRACT ADDRESSES:");
    console.log(`   Silvanus Token (Proxy): ${deploymentResults.silvanus}`);
    console.log(`   TokenTimelock (Grant Wallet): ${deploymentResults.timelock}`);
    console.log(`   GreenRewardDistributor (Proxy): ${deploymentResults.distributor}`);
    console.log(`   SVNPresale: ${deploymentResults.presale}`);
    console.log("=" .repeat(60));
    console.log("🔗 IMPORTANT LINKS:");
    console.log(`   Network: ${network.name} (${network.chainId})`);
    console.log(`   Deployer: ${deployerAddress}`);
    console.log(`   TokenTimelock Release: ${releaseDate.toISOString()}`);
    console.log("=" .repeat(60));
    
    const deploymentInfo = {
      network: network.name,
      chainId: network.chainId.toString(),
      deployer: deployerAddress,
      timestamp: new Date().toISOString(),
      contracts: deploymentResults,
      tokenAllocations: {
        presale: ethers.formatEther(PRESALE_ALLOCATION),
        rewards: ethers.formatEther(REWARDS_ALLOCATION),
        devTreasury: ethers.formatEther(DEV_TREASURY_ALLOCATION),
        liquidity: ethers.formatEther(LIQUIDITY_ALLOCATION),
        partnerships: ethers.formatEther(PARTNERSHIPS_ALLOCATION),
        projectSupport: ethers.formatEther(PROJECT_SUPPORT_ALLOCATION)
      },
      timelockReleaseTime: releaseTime,
      timelockReleaseDate: releaseDate.toISOString()
    };
    
    const fs = require('fs');
    const deploymentFileName = `deployment-${network.name}-${Date.now()}.json`;
    fs.writeFileSync(deploymentFileName, JSON.stringify(deploymentInfo, null, 2));
    console.log(`💾 Deployment info saved to: ${deploymentFileName}`);

  } catch (error) {
    console.error("❌ DEPLOYMENT FAILED!");
    console.error("Error:", error.message);
    
    if (error.transaction) {
      console.error("Transaction hash:", error.transaction.hash);
    }
    
    process.exitCode = 1;
  }
}

main().catch((error) => {
  console.error("❌ Deployment script error:", error);
  process.exitCode = 1;
});
