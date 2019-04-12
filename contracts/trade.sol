pragma solidity ^0.5.0;
// pragma solidity ^0.4.17;

contract Trade {

  //initialize balances mapping
  mapping (address => uint256) skins;

  //allows anyone to deposit funds
  function makeDeposit() public payable {
    skins[msg.sender] += msg.value;
  }

  //allows anyone to check their balance
  function checkSkins() view public returns (uint256 skins){
    return skins[msg.sender];
  }

  //allows anyone to withdraw funds, provided they hace claim to that amount
  function makeWithdrawal(uint256 amount) public returns (bool success) {
    // todo: figure out how to do membership check in solidity 
    if (amount in skins[msg.sender]) {
      skins[msg.sender] -= amount;
      msg.sender.transfer(amount);
      return true;
    } else {
      return false;
    }
  }

  // TODO : implement trade functionality with makeWithdrawal, makeDeposit function trade()

  
  //fallback, to account for calls to functions nonexistent within contract
  function () public payable {
    revert();
  }

}
