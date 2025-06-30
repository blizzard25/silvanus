from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv("SEPOLIA_RPC_URL")))
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
TOKEN_ADDRESS = "0x8f4FB6498A4D90FBc19c5b0b15F43869D7818Caa"  # Silvanus token address

ABI = [
    {
        "constant": True,
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    }
]

token = w3.eth.contract(address=TOKEN_ADDRESS, abi=ABI)

balance_wei = token.functions.balanceOf(WALLET_ADDRESS).call()
decimals = token.functions.decimals().call()
balance = balance_wei / (10 ** decimals)

print(f"Silvanus balance for {WALLET_ADDRESS}: {balance:.4f} SVN")
