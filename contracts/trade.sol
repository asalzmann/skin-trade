pragma solidity ^0.5.1;

contract Trade {

    /* State variables */
    uint256 balances;
    address owner;
    address payable seller;
    address payable buyer;
    uint256 assetID;
    uint256 price;

    /* Modifiers */
    modifier ownerOnly() {if (msg.sender == owner) _;}
    modifier sellerOnly() {if (msg.sender == seller) _;}
    modifier buyerOnly() {if (msg.sender == buyer) _;}

    /* Events */
    event Deposited(address indexed payee, uint256 weiAmount);
    event TradeSuccess(address indexed seller, uint256 weiAmountPaid, address indexed buyer, uint256 weiAmountReturned);
    event TradeFailure(address indexed buyer, uint256 weiAmountReturned);

    constructor(address payable _seller, address payable _buyer, uint256 _assetID, uint256 _price) public payable {
        owner   = msg.sender;
        seller  = _seller;
        buyer   = _buyer;
        assetID = _assetID;
        price = _price;
    }

    /**
     * @dev Stores the sent amount as deposit from the buyer.
     */
    function makeDeposit() public payable buyerOnly {
        uint256 amount = msg.value;
        balances = balances + (amount);

        emit Deposited(msg.sender, amount);
    }


    /**
     * @dev Allows anyone to check current amount paid by buyer.
     */
    function checkbalances() view public returns (uint256) {
        return balances;
    }

    /**
     * @dev Returns true if buyer has paid at least trade price.
     */
    function readyToTrade() view public returns (bool) {
        return checkbalances() >= price;
    }

    /**
     * @dev Allows seller to cancel trade, returns payment to buyer, and asset to seller.
     */
    function cancelTrade() public sellerOnly {
        executeTradeFailure();
    }

    /**
     * @dev Pays out seller on trade success.
     */
    function executeTradeSuccess() public ownerOnly {
        uint256 payment = balances;
        uint256 weiReturned = balances - price;
        balances = 0;

        seller.transfer(payment);
        buyer.transfer(weiReturned);

        emit TradeSuccess(seller, payment, buyer, weiReturned);
    }

    /**
     * @dev Returns deposit to buyer on trade failure.
     */
    function executeTradeFailure() public ownerOnly {
        uint256 payment = balances;
        balances = 0;

        buyer.transfer(payment);

        emit TradeFailure(buyer, payment);
    }

    function () external payable {
        revert();
    }

}
