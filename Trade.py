import js2py
import steampy 
import time
from web3 import Web3, HTTPProvider
import contract_abi
from steampy.client import SteamClient, Asset
from steampy.utils import GameOptions

#contract_address     = [YOUR CONTRACT ADDRESS]
wallet_private_key   = '1234rtgfde4567uhgfr67uj' # TODO : replace with a real private key 
wallet_address       = 'hgt67uhgfrtyujnbgtyuj' # TODO : replace with a real wallet address 
YOUR_INFURA_URL = "what is this ?????"

w3 = Web3(HTTPProvider([YOUR_INFURA_URL]))
w3.eth.enable_unaudited_features()


# todo : add infor to contract_abi.py from remix 
contract_address = '1234rtgfde4567uhgfr67uj' # TODO : Add contract address from remix 
contract = w3.eth.contract(address = contract_address, abi = contract_abi.abi)

# Example of a test trade 
# during sign up, steam account -> ETH wallet 

# User 1 
# In our app, User 1's credentials are provided on sign up 
USER_1_STEAM_ACCOUNT = 'user1'
USER_1_STEAM_PASSWORD = 'password'
USER_1_ETH_ADDR = '1234rtgfde4567uhgfr67uj' # TODO : replace with a real ETH address 

# User 2 
# In our app, User 2's credentials are provided on sign up 
USER_2_STEAM_ACCOUNT = 'user2'
USER_2_STEAM_PASSWORD = 'password'
USER_1_ETH_ADDR = 'hgfr5678ujhgfrtyujnbgtyu' #  TODO : replace with a real ETH address 

# Intermediary 
# We have the intermediary credentials 

# Parties agree on price & item 
# Example prices agreed on 
USER_1_BID = 10.0
USER_2_SELL_PRICE = 10.0
itemID = 1234

# deploy smart contract @params : ETH UID1, ETH UID2, itemid, price


# timeout 
timeout = time.time() + 60*10   # 10 minutes from now


if USER_1_BID >= USER_2_SELL_PRICE:

	while time.time() < timeout: # run 10 min

		if checkIfTradeFunded(contract):

			success = executeTrade(USER_1_STEAM_ACCOUNT, USER_2_STEAM_PASSWORD, itemID)

			if success:
				#transfer funds from buyer -> seller in smart contract 
				transferFundsToSeller(contract)
			else: 
				#transfer funds back to the buyer 
				transferFundsToBuyer(contract)
				return False # trade failed 
		else:
			return False 
	return True
else:
	return False


def checkIfTradeFunded(contract):
    return contract.functions.readyToTrade().call()

def transferFundsToSeller(contract):

    nonce = w3.eth.getTransactionCount(wallet_address)

    txn_dict = contract.functions.executeTradeSuccess().buildTransaction({
        'chainId': 3,
        'gas': 140000,
        'gasPrice': w3.toWei('40', 'gwei'),
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=wallet_private_key)

    result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    tx_receipt = w3.eth.getTransactionReceipt(result)

    count = 0
    while tx_receipt is None and (count < 30):

        time.sleep(10)

        tx_receipt = w3.eth.getTransactionReceipt(result)

        print(tx_receipt)


    if tx_receipt is None:
        return {'status': 'failed', 'error': 'timeout'}

    processed_receipt = contract.events.TradeSuccess().processReceipt(tx_receipt)

    print(processed_receipt)
   
    return {'status': 'added', 'processed_receipt': processed_receipt}
	

def transferFundsToBuyer(contract):
	#return contract.functions.executeTradeFailure().call() 
	nonce = w3.eth.getTransactionCount(wallet_address)

    txn_dict = contract.functions.executeTradeFailure().buildTransaction({
        'chainId': 3,
        'gas': 140000,
        'gasPrice': w3.toWei('40', 'gwei'),
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=wallet_private_key)

    result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    tx_receipt = w3.eth.getTransactionReceipt(result)

    count = 0
    while tx_receipt is None and (count < 30):

        time.sleep(10)

        tx_receipt = w3.eth.getTransactionReceipt(result)

        print(tx_receipt)


    if tx_receipt is None:
        return {'status': 'failed', 'error': 'timeout'}
    # not sure about this event thing 
    processed_receipt = contract.events.TradeFailure().processReceipt(tx_receipt)

    print(processed_receipt)
   
    return {'status': 'added', 'processed_receipt': processed_receipt}


def executeTrade(u1, u2, itemID):
	# todo 
	# u1 makes offer 
	# u2 accepts offer 
	return

# buyer funds the trade 
# while time < 10m
	# if trade is funded
	# 	execute trade (transfer item from seller to buyer) 
	# 	if success:
	# 		transfer funds from buyer -> seller in smart contract 
	#	else: 
	# 		transfer funds back to the buyer 
	# 		return
	# else:
	# 	pass 
# return 

