const { expect } = require("chai");
const { ethers, upgrades } = require("hardhat");

function toEther(amount) {
  return ethers.parseEther(amount.toString());
}

describe("Silvanus", function () {
  let Silvanus, token, owner, addr1, addr2, grantWallet;

  beforeEach(async function () {
    [owner, addr1, addr2, grantWallet] = await ethers.getSigners();
    Silvanus = await ethers.getContractFactory("Silvanus");
    token = await upgrades.deployProxy(
      Silvanus,
      [toEther(1000)],
      { initializer: "initialize" }
    );
    await token.waitForDeployment();
    
    await token.setBurnRate(50); // 0.5% burn rate
    await token.setGrantWallet(grantWallet.address);
  });

  it("should assign the total supply to the owner", async function () {
    const ownerBalance = await token.balanceOf(owner.address);
    expect(ownerBalance).to.equal(toEther(1000));
  });

  it("should transfer tokens between accounts with 0.5% redirected to grant wallet", async function () {
    const transferAmount = toEther(100);
    const expectedBurn = transferAmount * 50n / 10000n; // 0.5%
    const expectedReceive = transferAmount - expectedBurn;

    await token.transfer(addr1.address, transferAmount);

    const addr1Balance = await token.balanceOf(addr1.address);
    const ownerBalance = await token.balanceOf(owner.address);
    const grantWalletBalance = await token.balanceOf(grantWallet.address);
    const totalSupply = await token.totalSupply();

    expect(addr1Balance).to.equal(expectedReceive);
    expect(ownerBalance).to.equal(toEther(1000) - transferAmount);
    expect(grantWalletBalance).to.equal(expectedBurn);
    expect(totalSupply).to.equal(toEther(1000)); // Total supply unchanged (redirected, not burned)
  });

  it("should fail if sender doesn’t have enough tokens", async function () {
    await expect(
      token.connect(addr1).transfer(owner.address, toEther(1))
    ).to.be.revertedWithCustomError(token, "ERC20InsufficientBalance");
  });

  it("should update balances correctly after multiple transfers", async function () {
    // Transfer 100 to addr1 (redirect 0.5 to grant wallet)
    await token.transfer(addr1.address, toEther(100));
    // Transfer 50 to addr2 (redirect 0.25 to grant wallet)
    await token.transfer(addr2.address, toEther(50));

    const expectedBurn1 = toEther(100) * 50n / 10000n; // 0.5%
    const expectedBurn2 = toEther(50) * 50n / 10000n;

    const expectedAddr1 = toEther(100) - expectedBurn1;
    const expectedAddr2 = toEther(50) - expectedBurn2;

    const addr1Balance = await token.balanceOf(addr1.address);
    const addr2Balance = await token.balanceOf(addr2.address);
    const grantWalletBalance = await token.balanceOf(grantWallet.address);
    const totalSupply = await token.totalSupply();

    expect(addr1Balance).to.equal(expectedAddr1);
    expect(addr2Balance).to.equal(expectedAddr2);

    const totalRedirected = expectedBurn1 + expectedBurn2;
    expect(grantWalletBalance).to.equal(totalRedirected);
    expect(totalSupply).to.equal(toEther(1000)); // Total supply unchanged (redirected, not burned)
  });

  it("should exclude initial mint from burn mechanism", async function () {
    const newToken = await upgrades.deployProxy(
      Silvanus,
      [toEther(2000)],
      { initializer: "initialize" }
    );
    await newToken.waitForDeployment();
    
    await newToken.setBurnRate(50); // 0.5% burn rate
    await newToken.setGrantWallet(grantWallet.address);

    const ownerBalance = await newToken.balanceOf(owner.address);
    const grantWalletBalance = await newToken.balanceOf(grantWallet.address);
    const totalSupply = await newToken.totalSupply();

    expect(ownerBalance).to.equal(toEther(2000));
    expect(grantWalletBalance).to.equal(0); // No tokens redirected during mint
    expect(totalSupply).to.equal(toEther(2000));
  });
});
