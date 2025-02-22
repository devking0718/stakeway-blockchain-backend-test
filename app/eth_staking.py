from web3 import Web3
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class EthereumStaking:
    def __init__(self):
        # Connect to Sepolia testnet via Infura
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('SEPOLIA_RPC_URL')))
        
        # Load account from private key
        self.account = self.w3.eth.account.from_key(os.getenv('PRIVATE_KEY'))
        
        # Mock staking contract address (replace with actual contract address if available)
        self.staking_contract_address = os.getenv('STAKING_CONTRACT_ADDRESS')
        
        # Basic ABI for staking (modify based on actual contract)
        self.contract_abi = json.loads('''[
            {
                "inputs": [],
                "name": "stake",
                "outputs": [],
                "stateMutability": "payable",
                "type": "function"
            }
        ]''')
        
        self.contract = self.w3.eth.contract(
            address=self.staking_contract_address,
            abi=self.contract_abi
        )

    def get_balance(self, address):
        """Query the balance of a given wallet address"""
        balance_wei = self.w3.eth.get_balance(address)
        balance_eth = self.w3.from_wei(balance_wei, 'ether')
        return balance_eth

    def simulate_staking(self, amount_eth):
        """Simulate a staking transaction"""
        try:
            # Convert ETH to Wei
            amount_wei = self.w3.to_wei(amount_eth, 'ether')
            
            # Build the transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            transaction = self.contract.functions.stake().build_transaction({
                'from': self.account.address,
                'value': amount_wei,
                'gas': 200000,  # Adjust gas limit as needed
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
            })
            
            # Sign the transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, 
                self.account.key
            )
            
            # Send the transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'block_number': tx_receipt['blockNumber']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

def main():
    staking = EthereumStaking()
    
    # Example usage
    wallet_address = os.getenv('WALLET_ADDRESS')
    
    # Check balance
    balance = staking.get_balance(wallet_address)
    print(f"Current balance: {balance} ETH")
    
    # Simulate staking 0.1 ETH
    result = staking.simulate_staking(0.1)
    
    if result['success']:
        print(f"Staking transaction successful!")
        print(f"Transaction hash: {result['transaction_hash']}")
        print(f"Block number: {result['block_number']}")
    else:
        print(f"Staking failed: {result['error']}")

if __name__ == "__main__":
    main() 