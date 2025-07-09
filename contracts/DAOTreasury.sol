// SPDX-License-Identifier: MIT
pragma solidity ^0.8.22;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract DAOTreasury is Ownable {
    IERC20 public immutable token;

    event GrantReleased(address recipient, uint256 amount);

    constructor(address _token) {
        require(_token != address(0), "Invalid token address");
        token = IERC20(_token);
    }

    /// @notice Release tokens to a recipient — callable only by owner (DAO)
    function releaseGrant(address recipient, uint256 amount) external onlyOwner {
        require(recipient != address(0), "Invalid recipient");
        require(token.balanceOf(address(this)) >= amount, "Insufficient balance");

        token.transfer(recipient, amount);
        emit GrantReleased(recipient, amount);
    }

    /// @notice View balance of tokens held by treasury
    function balance() external view returns (uint256) {
        return token.balanceOf(address(this));
    }
}
