// SPDX-License-Identifier: MIT
pragma solidity ^0.8.22;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts-upgradeable/access/Ownable2StepUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";

contract GreenRewardDistributor is Initializable, Ownable2StepUpgradeable, UUPSUpgradeable {
    IERC20 public rewardToken;
    uint256 public baseReward;
    uint256 public totalGreenEvents;

    mapping(address => uint256) public totalClaimed;
    mapping(address => uint256) public pendingRewards;

    bool public claimModeEnabled;

    event RewardIssued(address indexed user, uint256 score, uint256 adjustedReward);

    function initialize(address tokenAddress, uint256 _baseReward) public initializer {
        __Ownable_init(msg.sender); 
        __Ownable2Step_init();
        __UUPSUpgradeable_init();

        rewardToken = IERC20(tokenAddress);
        baseReward = _baseReward;
        claimModeEnabled = false;
    }

    /// @notice Owner-only reward function. If `claimModeEnabled` is true, it queues the reward instead of sending it.
    function reward(address user, uint256 score) external onlyOwner {
        require(score > 0, "Score must be positive");

        totalGreenEvents += 1;

        uint256 denominator = log10(totalGreenEvents + 10);
        uint256 adjustedReward = (score * baseReward) / denominator;

        if (claimModeEnabled) {
            pendingRewards[user] += adjustedReward;
        } else {
            require(
                rewardToken.balanceOf(address(this)) >= adjustedReward,
                "Insufficient reward balance"
            );
            rewardToken.transfer(user, adjustedReward);
            totalClaimed[user] += adjustedReward;
        }

        emit RewardIssued(user, score, adjustedReward);
    }

    /// @notice Allows users to manually claim their queued rewards
    function claimReward() external {
        require(claimModeEnabled, "Claiming is not enabled");
        uint256 amount = pendingRewards[msg.sender];
        require(amount > 0, "Nothing to claim");

        pendingRewards[msg.sender] = 0;

        require(
            rewardToken.balanceOf(address(this)) >= amount,
            "Insufficient contract balance"
        );

        rewardToken.transfer(msg.sender, amount);
        totalClaimed[msg.sender] += amount;

        emit RewardIssued(msg.sender, 0, amount); // Score 0 used for claims
    }

    function setClaimModeEnabled(bool enabled) external onlyOwner {
        claimModeEnabled = enabled;
    }

    function updateBaseReward(uint256 newBaseReward) external onlyOwner {
        baseReward = newBaseReward;
    }

    function withdrawTokens(uint256 amount) external onlyOwner {
        rewardToken.transfer(msg.sender, amount);
    }

    function log10(uint256 x) internal pure returns (uint256) {
        uint256 result = 0;
        while (x >= 10) {
            x /= 10;
            result++;
        }
        return result + 1;
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyOwner {}
}
