import requests
import random
import json
import time
import os
from flask import Flask, render_template, session, redirect, url_for, escape, request
import steampy
import time
from web3 import Web3, HTTPProvider
import contract_abi
from steampy.client import SteamClient, Asset
from steampy.utils import GameOptions


app = Flask(__name__, static_folder='./build/static', template_folder='./build')
app.secret_key = os.environ['SECRET']

wallet_private_key   = os.environ['wallet_private']
wallet_address       = os.environ['wallet_address']
YOUR_INFURA_URL      = os.environ['INFURA']

w3 = Web3(HTTPProvider([YOUR_INFURA_URL]))
w3.eth.enable_unaudited_features()


@app.route('/trade', methods=['POST'])
def t():
    contract = w3.eth.contract(abi = contract_abi.abi)
    deployed_contract = None

    user1 = request.form['seller']
    user2 = request.form['buyer']

    # User 1: Seller
    # In our app, User 1's credentials are provided on sign up
    USER_1_STEAM_ACCOUNT = user1.steam
    USER_1_ETH_ADDR = user1.eth

    # User 2: Buyer
    # In our app, User 2's credentials are provided on sign up
    USER_2_STEAM_ACCOUNT = user2.steam
    USER_2_ETH_ADDR = user2.eth

    # We already have the intermediary credentials

    # Parties agree on price & item
    USER_1_BID = user1.bid
    USER_2_SELL_PRICE = user2.sell
    item_ID = request.form['itemUID']

    # timeout
    timeout = time.time() + 60*10   # 10 minutes from now

    if USER_1_BID >= USER_2_SELL_PRICE:
        # deploy smart contract @params : ETH UID1, ETH UID2, itemid, price
        tx_hash = contract.constructor.transact({
            arguments: [USER_1_ETH_ADDR, USER_2_ETH_ADDR, item_ID, USER_2_SELL_PRICE]
        })

        # Wait for the transaction to be mined, and get the transaction receipt
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

        deployed_contract = w3.eth.contract(
            address=tx_receipt.contractAddress,
            abi=contract_abi.abi,
        )

        while time.time() < timeout: # run 10 min

            if checkIfTradeFunded(contract):

                success = executeTrade(user1, user2, item_ID)

                if success:
                    #transfer funds from buyer -> seller in smart contract
                    return transferFundsToSeller(contract)
                else:
                    #transfer funds back to the buyer
                    return transferFundsToBuyer(contract)
            else:
                time.sleep(10)
        return {'status': 'failed', 'error': 'timeout'}
    else:
        return {'status': 'failure', 'error': 'invalid price'}


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

    if tx_receipt is None:
        return {'status': 'failed', 'error': 'timeout'}

    processed_receipt = contract.events.TradeSuccess().processReceipt(tx_receipt)
    print(processed_receipt)
    return {'status': 'success', 'processed_receipt': processed_receipt}


def transferFundsToBuyer(contract):
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

    if tx_receipt is None:
        return {'status': 'failed', 'error': 'timeout'}
    processed_receipt = contract.events.TradeFailure().processReceipt(tx_receipt)
    print(processed_receipt)
    return {'status': 'failed', 'processed_receipt': processed_receipt}


def getTradeID(u1, u2, item_ID):
    return str(hash(u1)) + str(hash(u2)) + str(hash(item_ID))
def executeTrade(u1, u2, item_ID):
    success = False
    MY_API_KEY = os.environ['MY_API_KEY']
    PATH_TO_STEAMGUARD_FILE = os.environ['PATH_TO_STEAMGUARD_FILE']
    OFFER_NAME = getTradeID(u1, u2, item_ID)

    u1_username = u1.steam
    u1_password = u1.pwd
    u1_id = u1.steam_ID

    u2_username = u2.steam
    u2_password = u2.pwd
    u2_id = u2.steam_ID
    
    steam_client_u1 = SteamClient(MY_API_KEY)
    steam_client_u1.login(u1_username, u1_password, PATH_TO_STEAMGUARD_FILE)

    steam_client_u2 = SteamClient(MY_API_KEY)
    steam_client_u2.login(u2_username, u2_password, PATH_TO_STEAMGUARD_FILE)
    

    game = GameOptions.CS
    my_items = steam_client_u1.get_my_inventory(game)
    partner_items = steam_client_u1.get_partner_inventory(u2_id, game)
    my_first_item = next(iter(my_items.values()))
    partner_first_item = next(iter(partner_items.values()))
    my_asset = Asset(my_first_item['id'], game)
    partner_asset = Asset(partner_first_item['id'], game)
    retDict = steam_client_u1.make_offer([my_asset], [partner_asset], partner_id, OFFER_NAME)

    if retDict:
        tradeofferid = retDict['tradeofferid']
        steam_client_u2.accept_trade_offer(tradeofferid)

        success = True # return success

    steam_client_u1.logout()
    steam_client_u2.logout()  
    return success

    
