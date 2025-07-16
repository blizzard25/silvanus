const { expect } = require("chai");
const { ethers, upgrades } = require("hardhat");

function toEther(amount) {
  return ethers.parseEther(amount.toString());
}

describe("GreenRewardDistributor", function () {
  let Token, Distributor, token, distributor;
  let owner, user1, user2;

  beforeEach(async function () {
    [owner, user1, user2] = await ethers.getSigners();

    // Deploy token with upgradeable proxy
    Token = await ethers.getContractFactory("Silvanus");
    token = await upgrades.deployProxy(
      Token,
      [toEther(1000000)],
      { initializer: "initialize" }
    );
    await token.waitForDeployment();

    // Deploy distributor with UUPS proxy
    Distributor = await ethers.getContractFactory("GreenRewardDistributor");
    distributor = await upgrades.deployProxy(
      Distributor,
      [token.target, toEther(10)],
      { kind: "uups" }
    );
    await distributor.waitForDeployment();

    // Send reward tokens to the distributor
    await token.transfer(distributor.target, toEther(100000));
  });

  it("issues immediate rewards when claimMode is disabled", async function () {
    await distributor.reward(user1.address, 100); // score = 100

    const balance = await token.balanceOf(user1.address);
    expect(balance).to.be.gt(0);

    const claimed = await distributor.totalClaimed(user1.address);
    expect(claimed).to.equal(balance);
  });

  it("queues rewards when claimMode is enabled", async function () {
    await distributor.setClaimModeEnabled(true);
    await distributor.reward(user1.address, 100);

    const balance = await token.balanceOf(user1.address);
    expect(balance).to.equal(0);

    const pending = await distributor.pendingRewards(user1.address);
    expect(pending).to.be.gt(0);
  });

  it("allows users to claim pending rewards", async function () {
    await distributor.setClaimModeEnabled(true);
    await distributor.reward(user1.address, 100);

    const pending = await distributor.pendingRewards(user1.address);
    expect(pending).to.be.gt(0);

    await distributor.connect(user1).claimReward();

    const balance = await token.balanceOf(user1.address);
    expect(balance).to.equal(pending);

    const claimed = await distributor.totalClaimed(user1.address);
    expect(claimed).to.equal(pending);
  });

  it("prevents claimReward() if claim mode is disabled", async function () {
    await distributor.setClaimModeEnabled(true);
    await distributor.reward(user1.address, 100);
    await distributor.setClaimModeEnabled(false);

    await expect(
      distributor.connect(user1).claimReward()
    ).to.be.revertedWith("Claiming is not enabled");
  });

  it("fails if claimReward has nothing to claim", async function () {
    await distributor.setClaimModeEnabled(true);

    await expect(
      distributor.connect(user2).claimReward()
    ).to.be.revertedWith("Nothing to claim");
  });
});
