const { expect } = require("chai");
const { ethers, upgrades } = require("hardhat");

function toEther(amount) {
  return ethers.parseEther(amount.toString());
}

describe("SVNPresale", function () {
  let Token, Presale, token, presale;
  let owner, buyer1, buyer2;

  beforeEach(async function () {
    [owner, buyer1, buyer2] = await ethers.getSigners();

    // Deploy token
    Token = await ethers.getContractFactory("Silvanus");
    token = await Token.deploy(toEther(100000000)); // 100M tokens
    await token.waitForDeployment();

    // Deploy presale
    Presale = await ethers.getContractFactory("SVNPresale");
    presale = await Presale.deploy(token.target, toEther(0.000017)); // Tier 1 price
    await presale.waitForDeployment();

    // Transfer presale tokens to presale contract
    await token.transfer(presale.target, toEther(21000000)); // 21M tokens
  });

  it("allows users to purchase SVN with ETH", async function () {
    const ethAmount = toEther(1); // 1 ETH
    await presale.connect(buyer1).buyTokens({ value: ethAmount });

    const purchased = await presale.purchased(buyer1.address);
    expect(purchased).to.be.gt(0);
  });

  it("prevents claiming before presale ends", async function () {
    const ethAmount = toEther(0.5);
    await presale.connect(buyer1).buyTokens({ value: ethAmount });

    await expect(
      presale.connect(buyer1).claimTokens()
    ).to.be.revertedWith("Presale not ended yet");
  });

  it("allows claim after presale ends", async function () {
    const ethAmount = toEther(0.5);
    await presale.connect(buyer1).buyTokens({ value: ethAmount });

    // End presale
    await presale.endPresale();

    const purchased = await presale.purchased(buyer1.address);

    const balanceBefore = await token.balanceOf(buyer1.address);
    await presale.connect(buyer1).claimTokens();
    const balanceAfter = await token.balanceOf(buyer1.address);

    expect(balanceAfter - balanceBefore).to.equal(purchased);
  });

  it("does not allow multiple claims", async function () {
    const ethAmount = toEther(0.5);
    await presale.connect(buyer1).buyTokens({ value: ethAmount });
    await presale.endPresale();

    await presale.connect(buyer1).claimTokens();

    await expect(
      presale.connect(buyer1).claimTokens()
    ).to.be.revertedWith("Nothing to claim");
  });

  it("rejects ETH if not enough tokens available", async function () {
    const maxAllocation = toEther(21000000); // full allocation
    await presale.connect(buyer1).buyTokens({ value: toEther(1000) }); // Attempt large buy

    const remaining = await token.balanceOf(presale.target);
    await token.transfer(owner.address, remaining); // Drain contract

    await expect(
      presale.connect(buyer2).buyTokens({ value: toEther(1) })
    ).to.be.revertedWith("Not enough tokens left");
  });
});
