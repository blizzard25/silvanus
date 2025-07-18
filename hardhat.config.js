require("@nomicfoundation/hardhat-toolbox");
require("@openzeppelin/hardhat-upgrades");
require("dotenv").config();

const { SEPOLIA_RPC_URL, MAINNET_RPC_URL, PRIVATE_KEY } = process.env;

module.exports = {
  solidity: "0.8.22",
  networks: {
    sepolia: {
      url: SEPOLIA_RPC_URL,
      accounts: [PRIVATE_KEY],
      gas: 8000000,
      gasPrice: 20000000000
    },
    mainnet: {
      url: MAINNET_RPC_URL || "https://eth-mainnet.g.alchemy.com/v2/your-api-key",
      accounts: [PRIVATE_KEY],
      gas: 8000000,
      gasPrice: 20000000000, // 20 gwei
    },
  },
};
