// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface ISilvanus {
    function transfer(address to, uint256 amount) external returns (bool);
}

contract GreenRewardDistributor {
    address public admin;
    ISilvanus public silvanus;

    modifier onlyAdmin() {
        require(msg.sender == admin, "Not authorized");
        _;
    }

    constructor(address _token) {
        admin = msg.sender;
        silvanus = ISilvanus(_token);
    }

    function reward(address user, uint256 amount) external onlyAdmin {
        require(silvanus.transfer(user, amount), "Transfer failed");
    }

    function updateAdmin(address newAdmin) external onlyAdmin {
        admin = newAdmin;
    }
}
