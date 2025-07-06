// SPDX-License-Identifier: MIT
pragma solidity ^0.8.22;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract SVNPresale is Ownable, ReentrancyGuard {
    IERC20 public immutable svnToken;

    uint256 public constant TIER1_PRICE = 0.000017 ether;
    uint256 public constant TIER2_PRICE = 0.000034 ether;
    uint256 public constant TIER3_PRICE = 0.000050 ether;

    uint256 public constant TIER1_CAP = 7_000_000 * 1e18;
    uint256 public constant TIER2_CAP = 14_000_000 * 1e18;
    uint256 public constant TOTAL_CAP = 21_000_000 * 1e18;

    uint256 public totalSold;
    bool public presaleEnded;
    mapping(address => uint256) public purchased;

    event TokensPurchased(address indexed buyer, uint256 amount, uint256 cost);
    event PresaleEnded(uint256 totalSold);

constructor(address _svnToken) Ownable(msg.sender) {
    require(_svnToken != address(0), "Invalid token address");
    svnToken = IERC20(_svnToken);
}


    function buyTokens() external payable nonReentrant {
        require(!presaleEnded, "Presale has ended");
        require(msg.value > 0, "Send ETH to buy tokens");

        uint256 remaining = TOTAL_CAP - totalSold;
        require(remaining > 0, "All tokens sold");

        (uint256 tokensToBuy, uint256 cost) = _calculateTokenAmount(msg.value);
        require(tokensToBuy > 0, "Zero token purchase");
        require(tokensToBuy <= remaining, "Exceeds presale allocation");

        purchased[msg.sender] += tokensToBuy;
        totalSold += tokensToBuy;

        emit TokensPurchased(msg.sender, tokensToBuy, cost);

        // Refund excess ETH if any
        if (msg.value > cost) {
            payable(msg.sender).transfer(msg.value - cost);
        }
    }

    function _calculateTokenAmount(uint256 ethAmount) internal view returns (uint256 tokens, uint256 cost) {
        uint256 remaining = ethAmount;
        tokens = 0;
        cost = 0;

        uint256 remainingTier1 = TIER1_CAP > totalSold ? TIER1_CAP - totalSold : 0;
        uint256 remainingTier2 = TIER2_CAP > totalSold ? TIER2_CAP - totalSold : 0;
        uint256 remainingTier3 = TOTAL_CAP - totalSold;

        if (remaining > 0 && remainingTier1 > 0) {
            uint256 purchasable = (remaining * 1e18) / TIER1_PRICE;
            uint256 actual = purchasable > remainingTier1 ? remainingTier1 : purchasable;
            uint256 tierCost = (actual * TIER1_PRICE) / 1e18;
            tokens += actual;
            cost += tierCost;
            remaining -= tierCost;
        }

        if (remaining > 0 && remainingTier2 > 0) {
            uint256 purchasable = (remaining * 1e18) / TIER2_PRICE;
            uint256 actual = purchasable > remainingTier2 ? remainingTier2 : purchasable;
            uint256 tierCost = (actual * TIER2_PRICE) / 1e18;
            tokens += actual;
            cost += tierCost;
            remaining -= tierCost;
        }

        if (remaining > 0 && remainingTier3 > 0) {
            uint256 purchasable = (remaining * 1e18) / TIER3_PRICE;
            uint256 actual = purchasable > remainingTier3 ? remainingTier3 : purchasable;
            uint256 tierCost = (actual * TIER3_PRICE) / 1e18;
            tokens += actual;
            cost += tierCost;
        }
    }

    function endPresale() external onlyOwner {
        require(!presaleEnded, "Presale already ended");
        presaleEnded = true;
        emit PresaleEnded(totalSold);
    }

    function withdrawETH() external onlyOwner {
        payable(msg.sender).transfer(address(this).balance);
    }

    function claimTokens() external nonReentrant {
        require(presaleEnded, "Presale not ended yet");
        uint256 amount = purchased[msg.sender];
        require(amount > 0, "Nothing to claim");
        purchased[msg.sender] = 0;
        require(svnToken.transfer(msg.sender, amount), "Token transfer failed");
    }
}
