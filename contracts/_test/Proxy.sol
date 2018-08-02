pragma solidity 0.4.24;

import "contracts/Interface/SchedulerInterface.sol";
import "contracts/Interface/TransactionRequestInterface.sol";

contract Proxy {
    SchedulerInterface public scheduler;
    address public receipient; 
    address public scheduledTransaction;
    address public owner;

    function Proxy(address _scheduler, address _receipient, uint _payout, uint _gasPrice, uint _delay) public payable {
        scheduler = SchedulerInterface(_scheduler);
        receipient = _receipient;
        owner = msg.sender;

        scheduledTransaction = scheduler.schedule.value(msg.value)(
            this,              // toAddress
            "",                     // callData
            [
                2000000,            // The amount of gas to be sent with the transaction.
                _payout,                  // The amount of wei to be sent.
                255,                // The size of the execution window.
                block.number + _delay,        // The start of the execution window.
                _gasPrice,    // The gasprice for the transaction
                12345 wei,          // The fee included in the transaction.
                224455 wei,         // The bounty that awards the executor of the transaction.
                20000 wei           // The required amount of wei the claimer must send as deposit.
            ]
        );
    }

    function () public payable {
        if (msg.value > 0) {
            receipient.transfer(msg.value);
        }
    }

    function sendOwnerEther(address _receipient) public {
        if (msg.sender == owner && _receipient != 0x0) {
            TransactionRequestInterface(scheduledTransaction).sendOwnerEther(_receipient);
        }   
    }
}