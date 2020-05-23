pragma solidity 0.4.20;

contract Fine {

   address public owner;
   // The address of the player and => the user info   
   function Fine() public{
      owner = msg.sender;
   }

   function kill() public {
      if(msg.sender == owner) selfdestruct(owner);
   }

   // To bet for a number between 1 and 10 both inclusive
   function pay() public payable {
      owner.transfer(msg.value);
   }
   // Fallback function in case someone sends ether to the contract so it doesn't get lost and to increase the treasury of this contract that will be distributed in each game
   function() public payable {}
}