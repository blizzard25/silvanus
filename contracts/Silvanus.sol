// SPDX-License-Identifier: MIT
pragma solidity ^0.8.22;

import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/Ownable2StepUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";

contract Silvanus is Initializable, ERC20Upgradeable, Ownable2StepUpgradeable, UUPSUpgradeable {
    uint256 public burnRate;

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers(); // disable initializer on implementation contract
    }

    function initialize(uint256 initialSupply) public initializer {
        __ERC20_init("Silvanus", "SVN");
       __Ownable_init(msg.sender);

__Ownable2Step_init();
        __UUPSUpgradeable_init();

        burnRate = 50; // 0.5%
        _mint(msg.sender, initialSupply);
    }

    // Override ERC20's _update instead of _transfer (as of OZ 5.x)
    function _update(address from, address to, uint256 value) internal virtual override {
        uint256 burnAmount = (value * burnRate) / 10000;
        uint256 sendAmount = value - burnAmount;

        if (burnAmount > 0) {
            super._update(from, address(0), burnAmount); // burn to zero address
        }
        super._update(from, to, sendAmount);
    }

    function setBurnRate(uint256 _rate) external onlyOwner {
        require(_rate <= 10000, "Burn rate too high");
        burnRate = _rate;
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyOwner {}
}
