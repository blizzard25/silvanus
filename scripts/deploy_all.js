const { ethers, upgrades } = require("hardhat");

async function main() {
  console.log("Starting Silvanus deployment...");

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
      throw new Error(`Missing required environment variable: ${name}`);
    }
    try {
      ethers.getAddress(address);
    } catch (error) {
      throw new Error(`Invalid address for ${name}: ${address}`);
    }
  }

  const TOTAL_SUPPLY = ethers.parseEther("100000000");
  const PRESALE_ALLOCATION = ethers.parseEther("21000000");
  const REWARDS_ALLOCATION = ethers.parseEther("40000000");
  const DEV_TREASURY_ALLOCATION = ethers.parseEther("12500000");
  const LIQUIDITY_ALLOCATION = ethers.parseEther("9000000");
  const PARTNERSHIPS_ALLOCATION = ethers.parseEther("7500000");
  const PROJECT_SUPPORT_ALLOCATION = ethers.parseEther("10000000");

  const deploymentResults = {};

  try {
    console.log("Deploying Silvanus Token...");
    const Silvanus = await ethers.getContractFactory("Silvanus");
    const silvanusProxy = await upgrades.deployProxy(Silvanus, [TOTAL_SUPPLY], {
      initializer: "initialize",
      kind: "uups"
    });
    await silvanusProxy.waitForDeployment();
    const silvanusAddress = await silvanusProxy.getAddress();
    deploymentResults.silvanus = silvanusAddress;
    console.log(`Silvanus Token deployed to: ${silvanusAddress}`);

    console.log("Deploying TokenTimelock...");
    const currentTime = Math.floor(Date.now() / 1000);
    const releaseTime = currentTime + (90 * 24 * 60 * 60);
    const TokenTimelock = await ethers.getContractFactory("TokenTimelock");
    const timelock = await TokenTimelock.deploy(
      silvanusAddress,
      TIMELOCK_BENEFICIARY,
      releaseTime
    );
    await timelock.waitForDeployment();
    const timelockAddress = await timelock.getAddress();
    deploymentResults.timelock = timelockAddress;
    console.log(`TokenTimelock deployed to: ${timelockAddress}`);

    console.log("Setting TokenTimelock as grantWallet...");
    const setGrantWalletTx = await silvanusProxy.setGrantWallet(timelockAddress);
    await setGrantWalletTx.wait();
    console.log("TokenTimelock set as grantWallet");

    console.log("Deploying GreenRewardDistributor...");
    const baseReward = ethers.parseEther("1");
    const GreenRewardDistributor = await ethers.getContractFactory("GreenRewardDistributor");
    const distributorProxy = await upgrades.deployProxy(
      GreenRewardDistributor,
      [silvanusAddress, baseReward],
      { 
        initializer: "initialize",
        kind: "uups"
      }
    );
    await distributorProxy.waitForDeployment();
    const distributorAddress = await distributorProxy.getAddress();
    deploymentResults.distributor = distributorAddress;
    console.log(`GreenRewardDistributor deployed to: ${distributorAddress}`);

    console.log("Deploying SVNPresale...");
    const SVNPresale = await ethers.getContractFactory("SVNPresale");
    const presale = await SVNPresale.deploy(silvanusAddress);
    await presale.waitForDeployment();
    const presaleAddress = await presale.getAddress();
    deploymentResults.presale = presaleAddress;
    console.log(`SVNPresale deployed to: ${presaleAddress}`);

    console.log("Distributing tokens...");
    const [deployer] = await ethers.getSigners();
    const deployerAddress = await deployer.getAddress();
    
    await (await silvanusProxy.transfer(presaleAddress, PRESALE_ALLOCATION)).wait();
    await (await silvanusProxy.transfer(distributorAddress, REWARDS_ALLOCATION)).wait();
    
    if (DEVELOPER_TREASURY.toLowerCase() !== deployerAddress.toLowerCase()) {
      await (await silvanusProxy.transfer(DEVELOPER_TREASURY, DEV_TREASURY_ALLOCATION)).wait();
    }
    
    await (await silvanusProxy.transfer(LIQUIDITY_POOL, LIQUIDITY_ALLOCATION)).wait();
    await (await silvanusProxy.transfer(PARTNERSHIPS, PARTNERSHIPS_ALLOCATION)).wait();
    await (await silvanusProxy.transfer(PROJECT_SUPPORT_AND_MARKETING, PROJECT_SUPPORT_ALLOCATION)).wait();
    
    console.log("Token distribution completed");

    console.log("DEPLOYMENT COMPLETED SUCCESSFULLY!");
    console.log("CONTRACT ADDRESSES:");
    console.log(`Silvanus Token (Proxy): ${deploymentResults.silvanus}`);
    console.log(`TokenTimelock (Grant Wallet): ${deploymentResults.timelock}`);
    console.log(`GreenRewardDistributor (Proxy): ${deploymentResults.distributor}`);
    console.log(`SVNPresale: ${deploymentResults.presale}`);

  } catch (error) {
    console.error("DEPLOYMENT FAILED!");
    console.error("Error:", error.message);
    process.exitCode = 1;
  }
}

main().catch((error) => {
  console.error("Deployment script error:", error);
  process.exitCode = 1;
});
