// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract SilvanusToken is ERC20, Ownable {
    uint256 public burnRate = 2; // burn 2% per transfer

    constructor(uint256 initialSupply) ERC20("SilvanusToken", "SVN") Ownable() {
        _mint(msg.sender, initialSupply);
    }

    function _transfer(address from, address to, uint256 amount) internal override {
        uint256 burnAmount = (amount * burnRate) / 100;
        uint256 sendAmount = amount - burnAmount;

        super._burn(from, burnAmount); // burn from sender
        super._transfer(from, to, sendAmount);
    }

    function setBurnRate(uint256 _rate) external onlyOwner {
        require(_rate <= 100, "Burn rate too high");
        burnRate = _rate;
    }
}
