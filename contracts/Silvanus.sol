// SPDX-License-Identifier: MIT
pragma solidity ^0.8.22;

import "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/ERC20PermitUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/ERC20VotesUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/Ownable2StepUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";

contract Silvanus is
    Initializable,
    ERC20PermitUpgradeable,
    ERC20VotesUpgradeable,
    Ownable2StepUpgradeable,
    UUPSUpgradeable
{
    uint256 public burnRate;
    address public grantWallet;

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(uint256 initialSupply) public initializer {
        __ERC20_init("Silvanus", "SVN");
        __ERC20Permit_init("Silvanus");
        __ERC20Votes_init();
        __Ownable_init(msg.sender);
        __Ownable2Step_init();
        __UUPSUpgradeable_init();

        burnRate = 0;
        _mint(msg.sender, initialSupply);
    }

    function setGrantWallet(address _wallet) external onlyOwner {
        require(_wallet != address(0), "Invalid address");
        grantWallet = _wallet;
    }

    function setBurnRate(uint256 _rate) external onlyOwner {
        require(_rate <= 10000, "Max 100%");
        burnRate = _rate;
    }

    /// ⚠️ Only override _update, not _mint/_burn
    function _update(address from, address to, uint256 value)
        internal
        override(ERC20Upgradeable, ERC20VotesUpgradeable)
    {
        if (from == address(0)) {
            // Minting
            super._update(from, to, value);
            return;
        }

        uint256 burnAmount = (value * burnRate) / 10000;
        uint256 sendAmount = value - burnAmount;

        if (burnAmount > 0) {
            require(grantWallet != address(0), "Grant wallet not set");
            super._update(from, grantWallet, burnAmount);
        }

        super._update(from, to, sendAmount);
    }

    /// 🧠 Required because ERC20Votes + Permit both use NoncesUpgradeable
    function nonces(address owner)
        public
        view
        override(ERC20PermitUpgradeable, NoncesUpgradeable)
        returns (uint256)
    {
        return super.nonces(owner);
    }

    function _authorizeUpgrade(address newImplementation)
        internal
        override
        onlyOwner
    {}
}
