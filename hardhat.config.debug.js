require("@nomicfoundation/hardhat-toolbox");
require("@openzeppelin/hardhat-upgrades");
require("dotenv").config();

const { SEPOLIA_RPC_URL, MAINNET_RPC_URL, PRIVATE_KEY, ETHERSCAN_API_KEY } = process.env;

module.exports = {
  solidity: {
    version: "0.8.22",
    settings: {
      evmVersion: "london",
      optimizer: {
        enabled: true,
      }
    }
  },
  networks: {
    hardhat: {
      forking: {
        url: MAINNET_RPC_URL,
        blockNumber: undefined
      },
      accounts: [
        {
          privateKey: PRIVATE_KEY,
          balance: "10000000000000000000"
        }
      ]
    },
    sepolia: {
      url: SEPOLIA_RPC_URL,
      accounts: [PRIVATE_KEY],
      gas: 8000000,
      gasPrice: 20000000000
    },
    mainnet: {
      url: MAINNET_RPC_URL,
      accounts: [PRIVATE_KEY],
      gas: 8000000,
      maxFeePerGas: 25000000000,
      maxPriorityFeePerGas: 2000000000,
    },
  },
  etherscan: {
    apiKey: {
      sepolia: ETHERSCAN_API_KEY,
      mainnet: ETHERSCAN_API_KEY
    }
  }
};
