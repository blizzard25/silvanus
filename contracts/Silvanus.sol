// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Silvanus is ERC20, Ownable {
    uint256 public burnRate = 50; // burn rate in basis points (0.5%)

    constructor(uint256 initialSupply) ERC20("Silvanus", "SVN") Ownable() {
        _mint(msg.sender, initialSupply);
    }

    function _transfer(address from, address to, uint256 amount) internal override {
        uint256 burnAmount = (amount * burnRate) / 10000;
        uint256 sendAmount = amount - burnAmount;

        super._burn(from, burnAmount); // burn from sender
        super._transfer(from, to, sendAmount);
    }

    function setBurnRate(uint256 _rate) external onlyOwner {
        require(_rate <= 10000, "Burn rate too high"); // max 100%
        burnRate = _rate;
    }
}
