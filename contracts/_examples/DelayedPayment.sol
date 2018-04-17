pragma solidity ^0.4.21;

import "contracts/Interface/SchedulerInterface.sol";

/// Example of using the Scheduler from a smart contract to delay a payment.
contract DelayedPayment {

    SchedulerInterface public scheduler;
    
    uint lockedUntil;
    address recipient;
    address public scheduledTransaction;

    function DelayedPayment(
        address _scheduler,
        uint    _numBlocks,
        address _recipient
    )  public payable {
        scheduler = SchedulerInterface(_scheduler);
        lockedUntil = block.number + _numBlocks;
        recipient = _recipient;

        scheduledTransaction = scheduler.schedule.value(0.1 ether)( // 0.1 ether is to pay for gas, bounty and fee
            this,                   // send to self
            "",                     // and trigger fallback function
            [
                200000,             // The amount of gas to be sent with the transaction.
                0,                  // The amount of wei to be sent.
                255,                // The size of the execution window.
                lockedUntil,        // The start of the execution window.
                20000000000 wei,    // The gasprice for the transaction (aka 20 gwei)
                20000000000 wei,    // The fee included in the transaction.
                20000000000 wei,         // The bounty that awards the executor of the transaction.
                30000000000 wei     // The required amount of wei the claimer must send as deposit.
            ]
        );
    }

    function () public payable {
        if (msg.value > 0) { //this handles recieving remaining funds sent while scheduling (0.1 ether)
            return;
        } else if (address(this).balance > 0) {
            payout();
        } else {
            revert();
        }
    }

    function payout()
        public returns (bool)
    {
        require(block.number >= lockedUntil);
        
        recipient.transfer(address(this).balance);
        return true;
    }
}