from nicegui import ui
from web3 import Web3
import os
from dotenv import load_dotenv

# --- Load environment ---
load_dotenv()
RPC_URL = os.getenv("SEPOLIA_RPC_URL")
TOKEN_ADDRESS = Web3.to_checksum_address(os.getenv("TOKEN_ADDRESS"))
ORIGINAL_SUPPLY = 1_000_000
BURN_RATE = 0.5

# --- Web3 setup ---
w3 = Web3(Web3.HTTPProvider(RPC_URL))
ABI = [
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
]
contract = w3.eth.contract(address=TOKEN_ADDRESS, abi=ABI)


def load_token_data():
    decimals = contract.functions.decimals().call()
    total_supply_wei = contract.functions.totalSupply().call()
    total_supply = total_supply_wei / (10 ** decimals)
    burned = ORIGINAL_SUPPLY - total_supply
    return total_supply, burned, BURN_RATE


@ui.page("/")
def dashboard():
    total, burned, rate = load_token_data()

    with ui.column().classes('min-h-screen w-full bg-gradient-to-br from-green-50 to-green-100 justify-center items-center p-8'):
        ui.label('Silvanus Dashboard').classes('text-4xl font-bold text-green-800 mb-8')

        with ui.row().classes('gap-6'):
            with ui.card().classes('p-6 bg-white shadow-xl rounded-xl'):
                ui.label('Total Supply').classes('text-sm text-gray-500')
                ui.label(f'{total:,.2f} SVN').classes('text-2xl font-bold text-green-700')

            with ui.card().classes('p-6 bg-white shadow-xl rounded-xl'):
                ui.label('Burned Tokens').classes('text-sm text-gray-500')
                ui.label(f'{burned:,.2f} SVN').classes('text-2xl font-bold text-red-600')

            with ui.card().classes('p-6 bg-white shadow-xl rounded-xl'):
                ui.label('Burn Rate').classes('text-sm text-gray-500')
                ui.label(f'{rate:.2f}%').classes('text-2xl font-bold text-yellow-600')

        ui.button('REFRESH', on_click=lambda: ui.open('/')).classes('mt-8 bg-green-600 text-white hover:bg-green-700')
        ui.link('→ Wallet Viewer', '/wallet').classes('mt-4 text-blue-600 hover:underline text-sm')


@ui.page('/wallet')
def wallet_viewer():
    with ui.column().classes('items-center justify-center min-h-screen bg-gray-50 p-8'):
        ui.label('GreenChain Wallet Viewer').classes('text-2xl font-bold text-green-700 mb-6')
        wallet_input = ui.input('Enter Wallet Address').props('outlined').classes('w-full max-w-md mb-4')
        balance_label = ui.label().classes('text-lg text-gray-700')
        error_label = ui.label().classes('text-red-600')

        def check_balance():
            try:
                address = Web3.to_checksum_address(wallet_input.value.strip())
                balance_wei = contract.functions.balanceOf(address).call()
                decimals = contract.functions.decimals().call()
                balance = balance_wei / (10 ** decimals)
                balance_label.text = f'Balance: {balance:.4f} SVN'
                error_label.text = ''
            except Exception as e:
                balance_label.text = ''
                error_label.text = f'Error: {str(e)}'

        ui.button('Check Balance', on_click=check_balance).classes('mt-2 bg-green-600 text-white hover:bg-green-700')
        ui.link('← Back to Dashboard', '/').classes('mt-6 text-blue-600 hover:underline')


ui.run()
