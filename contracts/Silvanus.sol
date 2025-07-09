// SPDX-License-Identifier: MIT
pragma solidity ^0.8.22;

import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/Ownable2StepUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";

contract Silvanus is Initializable, ERC20Upgradeable, Ownable2StepUpgradeable, UUPSUpgradeable {
    uint256 public burnRate;
    address public grantWallet;

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(uint256 initialSupply) public initializer {
        __ERC20_init("Silvanus", "SVN");
        __Ownable_init(msg.sender);
        __Ownable2Step_init();
        __UUPSUpgradeable_init();

        burnRate = 0; // Initially 0
        _mint(msg.sender, initialSupply);
    }

    // Override _update to split and redirect "burn"
    function _update(address from, address to, uint256 value) internal virtual override {
        uint256 burnAmount = (value * burnRate) / 10000;
        uint256 sendAmount = value - burnAmount;

        if (burnAmount > 0) {
            require(grantWallet != address(0), "Grant wallet not set");
            super._update(from, grantWallet, burnAmount); // Redirected to grant wallet
        }

        super._update(from, to, sendAmount);
    }

    function setBurnRate(uint256 _rate) external onlyOwner {
        require(_rate <= 10000, "Burn rate too high");
        burnRate = _rate;
    }

    function setGrantWallet(address _wallet) external onlyOwner {
        require(_wallet != address(0), "Invalid address");
        grantWallet = _wallet;
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyOwner {}
}
