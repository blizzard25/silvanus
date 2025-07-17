const { ethers } = require("hardhat");

async function main() {
  console.log("Starting token distribution...");

  const {
    TOKEN_ADDRESS,
    PRESALE_CONTRACT,
    REWARD_CONTRACT,
    DEVELOPER_TREASURY,
    PROJECT_SUPPORT_AND_MARKETING,
    PARTNERSHIPS,
    LIQUIDITY_POOL
  } = process.env;

  const requiredAddresses = {
    TOKEN_ADDRESS,
    PRESALE_CONTRACT,
    REWARD_CONTRACT,
    DEVELOPER_TREASURY,
    PROJECT_SUPPORT_AND_MARKETING,
    PARTNERSHIPS,
    LIQUIDITY_POOL
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

  const PRESALE_ALLOCATION = ethers.parseEther("21000000");
  const REWARDS_ALLOCATION = ethers.parseEther("40000000");
  const DEV_TREASURY_ALLOCATION = ethers.parseEther("12500000");
  const LIQUIDITY_ALLOCATION = ethers.parseEther("9000000");
  const PARTNERSHIPS_ALLOCATION = ethers.parseEther("7500000");
  const PROJECT_SUPPORT_ALLOCATION = ethers.parseEther("10000000");

  try {
    console.log("Connecting to Silvanus Token contract...");
    const Silvanus = await ethers.getContractFactory("Silvanus");
    const silvanusToken = Silvanus.attach(TOKEN_ADDRESS);
    
    console.log("Checking deployer balance...");
    const [deployer] = await ethers.getSigners();
    const deployerAddress = await deployer.getAddress();
    const deployerBalance = await silvanusToken.balanceOf(deployerAddress);
    console.log(`Deployer balance: ${ethers.formatEther(deployerBalance)} SVN`);

    const totalAllocation = PRESALE_ALLOCATION + REWARDS_ALLOCATION + DEV_TREASURY_ALLOCATION + 
                           LIQUIDITY_ALLOCATION + PARTNERSHIPS_ALLOCATION + PROJECT_SUPPORT_ALLOCATION;
    
    if (deployerBalance < totalAllocation) {
      throw new Error(`Insufficient balance. Need ${ethers.formatEther(totalAllocation)} SVN, have ${ethers.formatEther(deployerBalance)} SVN`);
    }

    console.log("Distributing tokens...");
    
    console.log(`Transferring ${ethers.formatEther(PRESALE_ALLOCATION)} SVN to Presale contract...`);
    await (await silvanusToken.transfer(PRESALE_CONTRACT, PRESALE_ALLOCATION)).wait();
    
    console.log(`Transferring ${ethers.formatEther(REWARDS_ALLOCATION)} SVN to Reward contract...`);
    await (await silvanusToken.transfer(REWARD_CONTRACT, REWARDS_ALLOCATION)).wait();
    
    if (DEVELOPER_TREASURY.toLowerCase() !== deployerAddress.toLowerCase()) {
      console.log(`Transferring ${ethers.formatEther(DEV_TREASURY_ALLOCATION)} SVN to Developer Treasury...`);
      await (await silvanusToken.transfer(DEVELOPER_TREASURY, DEV_TREASURY_ALLOCATION)).wait();
    } else {
      console.log("Developer Treasury is deployer address, skipping transfer");
    }
    
    console.log(`Transferring ${ethers.formatEther(LIQUIDITY_ALLOCATION)} SVN to Liquidity Pool...`);
    await (await silvanusToken.transfer(LIQUIDITY_POOL, LIQUIDITY_ALLOCATION)).wait();
    
    console.log(`Transferring ${ethers.formatEther(PARTNERSHIPS_ALLOCATION)} SVN to Partnerships...`);
    await (await silvanusToken.transfer(PARTNERSHIPS, PARTNERSHIPS_ALLOCATION)).wait();
    
    console.log(`Transferring ${ethers.formatEther(PROJECT_SUPPORT_ALLOCATION)} SVN to Project Support...`);
    await (await silvanusToken.transfer(PROJECT_SUPPORT_AND_MARKETING, PROJECT_SUPPORT_ALLOCATION)).wait();
    
    console.log("TOKEN DISTRIBUTION COMPLETED SUCCESSFULLY!");
    console.log("DISTRIBUTION SUMMARY:");
    console.log(`Presale Contract: ${ethers.formatEther(PRESALE_ALLOCATION)} SVN`);
    console.log(`Reward Contract: ${ethers.formatEther(REWARDS_ALLOCATION)} SVN`);
    console.log(`Developer Treasury: ${ethers.formatEther(DEV_TREASURY_ALLOCATION)} SVN`);
    console.log(`Liquidity Pool: ${ethers.formatEther(LIQUIDITY_ALLOCATION)} SVN`);
    console.log(`Partnerships: ${ethers.formatEther(PARTNERSHIPS_ALLOCATION)} SVN`);
    console.log(`Project Support: ${ethers.formatEther(PROJECT_SUPPORT_ALLOCATION)} SVN`);

  } catch (error) {
    console.error("TOKEN DISTRIBUTION FAILED!");
    console.error("Error:", error.message);
    process.exitCode = 1;
  }
}

main().catch((error) => {
  console.error("Distribution script error:", error);
  process.exitCode = 1;
});
