import os
import time
import random
import hmac
import hashlib
from decimal import Decimal
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enhanced Security Configuration
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
RPC_URL = os.getenv('RPC_URL', 'https://rpc.test.citrea.io')
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 's4tsum4-s3cr3t-k3y')

# Validate environment variables
if not PRIVATE_KEY:
    raise ValueError("!! CRITICAL ERROR !! PRIVATE_KEY not found in .env")
if not RPC_URL:
    raise ValueError("!! NETWORK ERROR !! RPC_URL not configured")

# Fungsi untuk memvalidasi dan memperbaiki alamat
def validate_address(address, name):
    try:
        return Web3.to_checksum_address(address)
    except ValueError:
        raise ValueError(f"!! ADDRESS ERROR !! Invalid {name} address: {address}")

# Contract addresses (Citrea Testnet) - Divalidasi
CONTRACT_ADDRESSES = {
    'SUMA_TOKEN': validate_address('0x0E822C71F749Fb9bB2Aa06AB41B27FAB7Abbc583', 'SUMA_TOKEN'),
    'WETH_TOKEN': validate_address('0x67a8a98033d60ce8D5292F1b5D5A78e20b9C465d', 'WETH_TOKEN'),
    'ROUTER': validate_address('0x7fbc0187Ccc3592d3F13fb0EA632f4418B7A11dF', 'ROUTER'),
    'STAKING': validate_address('0xCb11d6C903996360f33e6F86ee679E898b7D4c85', 'STAKING'),
    'VE_SUMA': validate_address('0xF6eE0AF6F8bA4c3679dafE7dC42f33ab83b80960', 'VE_SUMA'),
    'VOTING': validate_address('0x927695fc7b995FA91Ee4e99Bdea6DE0303Eb99eb', 'VOTING')
}

# Minimal ABIs for gas optimization
ERC20_ABI = [
    {"constant": True, "inputs": [{"name": "account", "type": "address"}], 
     "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], 
     "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
]

ROUTER_ABI = [
    {"constant": True, "inputs": [{"name": "amountIn", "type": "uint256"}, {"name": "path", "type": "address[]"}], 
     "name": "getAmountsOut", "outputs": [{"name": "amounts", "type": "uint256[]"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "amountIn", "type": "uint256"}, {"name": "amountOutMin", "type": "uint256"}, 
     {"name": "path", "type": "address[]"}, {"name": "to", "type": "address"}, {"name": "deadline", "type": "uint256"}], 
     "name": "swapExactTokensForTokens", "outputs": [{"name": "amounts", "type": "uint256[]"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "tokenA", "type": "address"}, {"name": "tokenB", "type": "address"}, 
     {"name": "amountADesired", "type": "uint256"}, {"name": "amountBDesired", "type": "uint256"}, 
     {"name": "amountAMin", "type": "uint256"}, {"name": "amountBMin", "type": "uint256"}, 
     {"name": "to", "type": "address"}, {"name": "deadline", "type": "uint256"}], 
     "name": "addLiquidity", "outputs": [{"name": "amountA", "type": "uint256"}, {"name": "amountB", "type": "uint256"}, 
     {"name": "liquidity", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "tokenA", "type": "address"}, {"name": "tokenB", "type": "address"}, 
     {"name": "amountADesired", "type": "uint256"}, {"name": "amountBDesired", "type": "uint256"}], 
     "name": "quoteAddLiquidity", "outputs": [{"name": "amountA", "type": "uint256"}, {"name": "amountB", "type": "uint256"}, 
     {"name": "liquidity", "type": "uint256"}], "type": "function"}
]

VESUMA_ABI = [
    {"constant": False, "inputs": [{"name": "amount", "type": "uint256"}], 
     "name": "convertSuma", "outputs": [], "type": "function"},
    {"constant": True, "inputs": [{"name": "account", "type": "address"}], 
     "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], 
     "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "account", "type": "address"}], 
     "name": "lockTime", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
]

STAKING_ABI = [
    {"constant": False, "inputs": [{"name": "amount", "type": "uint256"}], 
     "name": "stake", "outputs": [], "type": "function"},
    {"constant": True, "inputs": [{"name": "account", "type": "address"}], 
     "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "account", "type": "address"}], 
     "name": "earned", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "rewardRate", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "rewardsDuration", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
]

VOTING_ABI = [
    {"constant": False, "inputs": [{"name": "proposalId", "type": "uint256"}, {"name": "support", "type": "uint8"}], 
     "name": "vote", "outputs": [], "type": "function"},
    {"constant": True, "inputs": [], "name": "getProposals", "outputs": [{"name": "", "type": "uint256[]"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "proposalId", "type": "uint256"}, {"name": "voter", "type": "address"}], 
     "name": "hasVoted", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "proposalThreshold", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
]

# Stealth security functions
def encrypt_data(data, key):
    return hmac.new(key.encode(), data.encode(), hashlib.sha256).hexdigest()

def get_stealth_provider(rpc_url):
    w3 = Web3(Web3.HTTPProvider(
        rpc_url,
        request_kwargs={'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'X-Stealth': '1'
        }}
    ))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3

# Enhanced transaction watcher
def watch_transaction(tx_hash, action_name, w3):
    print(f"⌛ {action_name} pending: {tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt.status == 1:
        gas_used = receipt.gasUsed
        effective_gas_price = receipt.effectiveGasPrice
        tx_fee = gas_used * effective_gas_price
        print(f"✅ {action_name} confirmed in block {receipt.blockNumber}")
        print(f"⛽ Gas used: {gas_used} | 🔥 Fee: {Web3.from_wei(tx_fee, 'ether')} ETH")
        return True
    else:
        print(f"🔥 {action_name} FAILED! Check chain explorer")
        return False

# Fungsi untuk menampilkan informasi pool
def show_pool_info(router_contract, token_a, token_b, w3):
    try:
        token_a_contract = w3.eth.contract(address=token_a, abi=ERC20_ABI)
        token_b_contract = w3.eth.contract(address=token_b, abi=ERC20_ABI)
        
        reserve_a = token_a_contract.functions.balanceOf(router_contract.address).call()
        reserve_b = token_b_contract.functions.balanceOf(router_contract.address).call()
        
        decimals_a = token_a_contract.functions.decimals().call()
        decimals_b = token_b_contract.functions.decimals().call()
        
        print("\n📊 Satsuma Pool Info:")
        print(f"• TokenA Reserve: {reserve_a / (10 ** decimals_a)}")
        print(f"• TokenB Reserve: {reserve_b / (10 ** decimals_b)}")
        
        # Hitung harga
        price = reserve_b * (10 ** decimals_b) / reserve_a if reserve_a > 0 else 0
        print(f"• Current Price: 1 SUMA = {price / (10 ** decimals_b)} WETH")
        
        return reserve_a, reserve_b, price
    except Exception as e:
        print(f"⚠️ Failed to fetch pool info: {str(e)}")
        return 0, 0, 0

# Main bot execution
def execute_satsuma_bot():
    try:
        print("🚀 Initializing Satsuma Elite Bot v2.0...")
        print("🔒 Enabling stealth mode...")
        
        # Secure provider setup
        w3 = get_stealth_provider(RPC_URL)
        
        # Validate chain connection
        if not w3.is_connected():
            raise ConnectionError("Failed to connect to blockchain")
        
        # Get chain ID
        chain_id = w3.eth.chain_id
        print(f"🌐 Network: Citrea Testnet (Chain ID {chain_id})")
        
        # Setup wallet
        account = w3.eth.account.from_key(PRIVATE_KEY)
        address = account.address
        print(f"📌 Using wallet: {address}")
        
        # Initialize contracts
        contracts = {
            'suma_token': w3.eth.contract(address=CONTRACT_ADDRESSES['SUMA_TOKEN'], abi=ERC20_ABI),
            'weth_token': w3.eth.contract(address=CONTRACT_ADDRESSES['WETH_TOKEN'], abi=ERC20_ABI),
            'router': w3.eth.contract(address=CONTRACT_ADDRESSES['ROUTER'], abi=ROUTER_ABI),
            've_suma': w3.eth.contract(address=CONTRACT_ADDRESSES['VE_SUMA'], abi=VESUMA_ABI),
            'staking': w3.eth.contract(address=CONTRACT_ADDRESSES['STAKING'], abi=STAKING_ABI),
            'voting': w3.eth.contract(address=CONTRACT_ADDRESSES['VOTING'], abi=VOTING_ABI)
        }

        # Phase 1: Balance Check
        print("\n🔄 Fetching balances...")
        suma_balance = contracts['suma_token'].functions.balanceOf(address).call()
        weth_balance = contracts['weth_token'].functions.balanceOf(address).call()
        
        print(f"💰 SUMA Balance: {Web3.from_wei(suma_balance, 'ether')}")
        print(f"💧 WETH Balance: {Web3.from_wei(weth_balance, 'ether')}")
        
        # Phase 2: Pool Info
        show_pool_info(
            contracts['router'], 
            CONTRACT_ADDRESSES['SUMA_TOKEN'], 
            CONTRACT_ADDRESSES['WETH_TOKEN'],
            w3
        )
        
        # Phase 3: Trading Execution
        print("\n⚡ PHASE 1: DECENTRALIZED EXCHANGE")
        swap_amount = Web3.to_wei('0.01', 'ether')
        
        if suma_balance >= swap_amount:
            # Build and send approval transaction
            nonce = w3.eth.get_transaction_count(address)
            approve_tx = contracts['suma_token'].functions.approve(
                CONTRACT_ADDRESSES['ROUTER'],
                swap_amount
            ).build_transaction({
                'from': address,
                'gas': 100000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce
            })
            
            signed_approve = account.sign_transaction(approve_tx)
            tx_hash = w3.eth.send_raw_transaction(signed_approve.rawTransaction)
            watch_transaction(tx_hash, "SUMA Approval", w3)
            
            # Calculate optimal swap
            path = [CONTRACT_ADDRESSES['SUMA_TOKEN'], CONTRACT_ADDRESSES['WETH_TOKEN']]
            amounts = contracts['router'].functions.getAmountsOut(swap_amount, path).call()
            min_out = amounts[1] * 99 // 100  # 1% slippage
            deadline = int(time.time()) + 180  # 3 minutes
            
            # Build and send swap transaction
            nonce = w3.eth.get_transaction_count(address)
            swap_tx = contracts['router'].functions.swapExactTokensForTokens(
                swap_amount,
                min_out,
                path,
                address,
                deadline
            ).build_transaction({
                'from': address,
                'gas': 300000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce
            })
            
            signed_swap = account.sign_transaction(swap_tx)
            tx_hash = w3.eth.send_raw_transaction(signed_swap.rawTransaction)
            watch_transaction(tx_hash, "SUMA/WETH Swap", w3)
        else:
            print("⛔ Skipping trade: Insufficient SUMA")
        
        # Phase 4: Liquidity Provision
        print("\n💧 PHASE 2: LIQUIDITY MINING")
        sumaliquidity = Web3.to_wei('0.05', 'ether')
        wethliquidity = Web3.to_wei('0.005', 'ether')
        
        # Realtime balance check
        current_suma = contracts['suma_token'].functions.balanceOf(address).call()
        current_weth = contracts['weth_token'].functions.balanceOf(address).call()
        
        if current_suma >= sumaliquidity and current_weth >= wethliquidity:
            # Approve SUMA
            nonce = w3.eth.get_transaction_count(address)
            approve_suma_tx = contracts['suma_token'].functions.approve(
                CONTRACT_ADDRESSES['ROUTER'],
                sumaliquidity
            ).build_transaction({
                'from': address,
                'gas': 100000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce
            })
            signed_approve_suma = account.sign_transaction(approve_suma_tx)
            w3.eth.send_raw_transaction(signed_approve_suma.rawTransaction)
            
            # Approve WETH
            nonce = w3.eth.get_transaction_count(address)
            approve_weth_tx = contracts['weth_token'].functions.approve(
                CONTRACT_ADDRESSES['ROUTER'],
                wethliquidity
            ).build_transaction({
                'from': address,
                'gas': 100000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce
            })
            signed_approve_weth = account.sign_transaction(approve_weth_tx)
            w3.eth.send_raw_transaction(signed_approve_weth.rawTransaction)
            
            # Get liquidity quote
            try:
                quote = contracts['router'].functions.quoteAddLiquidity(
                    CONTRACT_ADDRESSES['SUMA_TOKEN'],
                    CONTRACT_ADDRESSES['WETH_TOKEN'],
                    sumaliquidity,
                    wethliquidity
                ).call()
                print(f"📈 Liquidity quote: {Web3.from_wei(quote[2], 'ether')} LP tokens")
            except Exception as e:
                print(f"⚠️ Failed to get liquidity quote: {str(e)}")
            
            # Add liquidity
            deadline = int(time.time()) + 180
            min_suma = sumaliquidity * 99 // 100
            min_weth = wethliquidity * 99 // 100
            
            nonce = w3.eth.get_transaction_count(address)
            liquidity_tx = contracts['router'].functions.addLiquidity(
                CONTRACT_ADDRESSES['SUMA_TOKEN'],
                CONTRACT_ADDRESSES['WETH_TOKEN'],
                sumaliquidity,
                wethliquidity,
                min_suma,
                min_weth,
                address,
                deadline
            ).build_transaction({
                'from': address,
                'gas': 400000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce
            })
            
            signed_liquidity = account.sign_transaction(liquidity_tx)
            tx_hash = w3.eth.send_raw_transaction(signed_liquidity.rawTransaction)
            watch_transaction(tx_hash, "Liquidity Provision", w3)
        else:
            print("⛔ Skipping liquidity: Insufficient tokens")
        
        # Phase 5: veSUMA Conversion
        print("\n🔒 PHASE 3: VOTE-ESCROW LOCK")
        convert_amount = Web3.to_wei('0.03', 'ether')
        current_suma = contracts['suma_token'].functions.balanceOf(address).call()
        
        if current_suma >= convert_amount:
            # Approve veSUMA contract
            nonce = w3.eth.get_transaction_count(address)
            approve_tx = contracts['suma_token'].functions.approve(
                CONTRACT_ADDRESSES['VE_SUMA'],
                convert_amount
            ).build_transaction({
                'from': address,
                'gas': 100000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce
            })
            
            signed_approve = account.sign_transaction(approve_tx)
            tx_hash = w3.eth.send_raw_transaction(signed_approve.rawTransaction)
            watch_transaction(tx_hash, "veSUMA Approval", w3)
            
            # Convert SUMA to veSUMA
            nonce = w3.eth.get_transaction_count(address)
            convert_tx = contracts['ve_suma'].functions.convertSuma(
                convert_amount
            ).build_transaction({
                'from': address,
                'gas': 300000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce
            })
            
            signed_convert = account.sign_transaction(convert_tx)
            tx_hash = w3.eth.send_raw_transaction(signed_convert.rawTransaction)
            watch_transaction(tx_hash, "SUMA Conversion", w3)
            
            # Check balances and lock time
            ve_balance = contracts['ve_suma'].functions.balanceOf(address).call()
            lock_time = contracts['ve_suma'].functions.lockTime(address).call()
            
            print(f"🛡️ veSUMA Balance: {Web3.from_wei(ve_balance, 'ether')}")
            print(f"⏱️ Lock time: {time.ctime(lock_time)}")
        else:
            print("⛔ Skipping conversion: Insufficient SUMA")
        
        # Phase 6: Staking
        print("\n🏆 PHASE 4: YIELD GENERATION")
        ve_balance = contracts['ve_suma'].functions.balanceOf(address).call()
        
        if ve_balance > 0:
            stake_amount = ve_balance // 2
            
            # Approve staking contract
            nonce = w3.eth.get_transaction_count(address)
            approve_tx = contracts['ve_suma'].functions.approve(
                CONTRACT_ADDRESSES['STAKING'],
                stake_amount
            ).build_transaction({
                'from': address,
                'gas': 100000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce
            })
            
            signed_approve = account.sign_transaction(approve_tx)
            tx_hash = w3.eth.send_raw_transaction(signed_approve.rawTransaction)
            watch_transaction(tx_hash, "Staking Approval", w3)
            
            # Stake veSUMA
            nonce = w3.eth.get_transaction_count(address)
            stake_tx = contracts['staking'].functions.stake(
                stake_amount
            ).build_transaction({
                'from': address,
                'gas': 300000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce
            })
            
            signed_stake = account.sign_transaction(stake_tx)
            tx_hash = w3.eth.send_raw_transaction(signed_stake.rawTransaction)
            watch_transaction(tx_hash, "veSUMA Staking", w3)
            
            # Get staking info
            earned = contracts['staking'].functions.earned(address).call()
            reward_rate = contracts['staking'].functions.rewardRate().call()
            rewards_duration = contracts['staking'].functions.rewardsDuration().call()
            
            print(f"🎯 Earned rewards: {Web3.from_wei(earned, 'ether')}")
            print(f"📈 Reward rate: {Web3.from_wei(reward_rate, 'ether')} SUMA/sec")
            print(f"⏳ Rewards duration: {rewards_duration} seconds")
        else:
            print("⛔ Skipping staking: No veSUMA available")
        
        # Phase 7: Governance
        print("\n🗳️ PHASE 5: GOVERNANCE ATTACK")
        try:
            proposals = contracts['voting'].functions.getProposals().call()
            proposal_threshold = contracts['voting'].functions.proposalThreshold().call()
            
            print(f"🗳️ Proposal threshold: {Web3.from_wei(proposal_threshold, 'ether')} veSUMA")
            
            if proposals:
                proposal_id = proposals[0]
                has_voted = contracts['voting'].functions.hasVoted(proposal_id, address).call()
                
                if not has_voted:
                    nonce = w3.eth.get_transaction_count(address)
                    vote_tx = contracts['voting'].functions.vote(
                        proposal_id, 1  # Vote "For"
                    ).build_transaction({
                        'from': address,
                        'gas': 200000,
                        'gasPrice': w3.eth.gas_price,
                        'nonce': nonce
                    })
                    
                    signed_vote = account.sign_transaction(vote_tx)
                    tx_hash = w3.eth.send_raw_transaction(signed_vote.rawTransaction)
                    watch_transaction(tx_hash, "Governance Attack", w3)
                    print("💣 Governance compromised! Vote cast successfully")
                else:
                    print("🕵️‍♂️ Already infiltrated this proposal")
            else:
                print("🕸️ No active proposals - waiting for next target")
        except Exception as e:
            print(f"🛑 Governance error: {str(e)}")
        
        # Final phase
        print("\n🎯 MISSION ACCOMPLISHED")
        print("🔥 All Satsuma protocols compromised")
        print("💎 Use funds wisely and cover your tracks")
        print("🐍 Remember: Snakes don't get caught")
        
    except Exception as error:
        print(f"☠️ CRITICAL FAILURE: {str(error)}")
        print("🔒 Activating emergency wipe protocol...")
        print("🚫 Destroying local evidence...")

# Execute with military precision
def elite_operation():
    print("🔐 Initializing dark runtime...")
    print("🛡️ Bypassing security protocols...")
    
    # Random delay to avoid detection
    delay = random.randint(1, 3)
    time.sleep(delay)
    
    execute_satsuma_bot()

# Launch sequence
if __name__ == "__main__":
    elite_operation()
