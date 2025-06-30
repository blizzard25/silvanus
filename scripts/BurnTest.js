const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("SilvanusToken with Burn", function () {
  let Token, token, owner, user;

  beforeEach(async function () {
    [owner, user] = await ethers.getSigners();

    Token = await ethers.getContractFactory("SilvanusToken");
    token = await Token.deploy(ethers.utils.parseEther("1000")); // 1000 SVN
    await token.deployed();
  });

  it("should burn 1% on transfer", async function () {
    const amount = ethers.utils.parseEther("100.0");
    const expectedBurn = ethers.utils.parseEther("1.0");
    const expectedReceive = ethers.utils.parseEther("99.0");

    await token.transfer(user.address, amount);

    const userBalance = await token.balanceOf(user.address);
    const burnBalance = await token.balanceOf("0x000000000000000000000000000000000000dEaD");
    const totalSupply = await token.totalSupply();

    expect(userBalance).to.equal(expectedReceive);
    expect(burnBalance).to.equal(expectedBurn);
    expect(totalSupply).to.equal(ethers.utils.parseEther("1000")); // totalSupply remains unchanged unless overridden
  });
});
