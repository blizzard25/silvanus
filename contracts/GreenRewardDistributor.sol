// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract GreenRewardDistributor is Ownable {
    IERC20 public rewardToken;
    uint256 public baseReward; // in wei
    uint256 public totalGreenEvents;

    mapping(address => uint256) public totalClaimed;

    event RewardIssued(address indexed user, uint256 score, uint256 adjustedReward);

    constructor(address tokenAddress, uint256 _baseReward) {
        rewardToken = IERC20(tokenAddress);
        baseReward = _baseReward; // e.g., 1e18 for 1 token
    }

    function reward(address user, uint256 score) external onlyOwner {
        require(score > 0, "Score must be positive");

        totalGreenEvents += 1;

        uint256 denominator = log10(totalGreenEvents + 10);
        uint256 adjustedReward = (score * baseReward) / denominator;

        require(rewardToken.balanceOf(address(this)) >= adjustedReward, "Insufficient reward balance");

        rewardToken.transfer(user, adjustedReward);
        totalClaimed[user] += adjustedReward;

        emit RewardIssued(user, score, adjustedReward);
    }

    // Integer log base 10
    function log10(uint256 x) internal pure returns (uint256) {
        uint256 result = 0;
        while (x >= 10) {
            x /= 10;
            result++;
        }
        return result + 1; // shift so log10(10) = 2
    }

    function updateBaseReward(uint256 newBaseReward) external onlyOwner {
        baseReward = newBaseReward;
    }

    function withdrawTokens(uint256 amount) external onlyOwner {
        rewardToken.transfer(msg.sender, amount);
    }
}
