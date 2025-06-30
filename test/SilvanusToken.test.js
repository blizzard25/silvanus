const { expect } = require("chai");
const { ethers } = require("hardhat");

function toEther(amount) {
  return ethers.parseEther(amount.toString());
}

describe("SilvanusToken", function () {
  let SilvanusToken, token, owner, addr1, addr2;

  beforeEach(async function () {
    [owner, addr1, addr2] = await ethers.getSigners();
    SilvanusToken = await ethers.getContractFactory("SilvanusToken");
    token = await SilvanusToken.deploy(toEther(1000));
    await token.waitForDeployment();
  });

  it("should assign the total supply to the owner", async function () {
    const ownerBalance = await token.balanceOf(owner.address);
    expect(ownerBalance).to.equal(toEther(1000));
  });

  it("should transfer tokens between accounts with 0.5% burn", async function () {
    const transferAmount = toEther(100);
    const expectedBurn = transferAmount * 50n / 10000n; // 0.5%
    const expectedReceive = transferAmount - expectedBurn;

    await token.transfer(addr1.address, transferAmount);

    const addr1Balance = await token.balanceOf(addr1.address);
    const ownerBalance = await token.balanceOf(owner.address);
    const totalSupply = await token.totalSupply();

    expect(addr1Balance).to.equal(expectedReceive);
    expect(ownerBalance).to.equal(toEther(1000) - transferAmount);
    expect(totalSupply).to.equal(toEther(1000) - expectedBurn);
  });

  it("should fail if sender doesn’t have enough tokens", async function () {
    await expect(
      token.connect(addr1).transfer(owner.address, toEther(1))
    ).to.be.revertedWith("ERC20: burn amount exceeds balance");
  });

  it("should update balances correctly after multiple transfers", async function () {
    // Transfer 100 to addr1 (burn 0.5)
    await token.transfer(addr1.address, toEther(100));
    // Transfer 50 to addr2 (burn 0.25)
    await token.transfer(addr2.address, toEther(50));

    const expectedBurn1 = toEther(100) * 50n / 10000n; // 0.5%
    const expectedBurn2 = toEther(50) * 50n / 10000n;

    const expectedAddr1 = toEther(100) - expectedBurn1;
    const expectedAddr2 = toEther(50) - expectedBurn2;

    const addr1Balance = await token.balanceOf(addr1.address);
    const addr2Balance = await token.balanceOf(addr2.address);
    const totalSupply = await token.totalSupply();

    expect(addr1Balance).to.equal(expectedAddr1);
    expect(addr2Balance).to.equal(expectedAddr2);

    const totalBurned = expectedBurn1 + expectedBurn2;
    expect(totalSupply).to.equal(toEther(1000) - totalBurned);
  });
});
