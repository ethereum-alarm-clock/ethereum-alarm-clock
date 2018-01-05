pragma solidity ^0.4.18;

import 'contracts/Interface/SchedulerInterface.sol';

/// Example of using the Scheduler from a smart contract to delay a payment.
contract DelayedPayment {

    SchedulerInterface public scheduler;

    uint lockedUntil;
    address recipient;

    function DelayedPayment(
        address _scheduler,
        uint    _numBlocks,
        address _recipient
    ) {
        scheduler = SchedulerInterface(_scheduler);
        lockedUntil = block.number + _numBlocks;
        recipient = _recipient;

        scheduler.schedule.value(2 ether)(
            recipient,              // toAddress
            "",                     // callData
            [
                2000000,            // The amount of gas to be sent with the transaction.
                0,                  // The amount of wei to be sent.
                255,                // The size of the execution window.
                lockedUntil,        // The start of the execution window.
                30000000000 wei,    // The gasprice for the transaction (aka 30 gwei)
                12345 wei,          // The donation included in the transaction.
                224455 wei,         // The payment included in the transaction.
                20000 wei           // The required amount of wei to claimer must send as deposit.
            ]
        );
    }

    function () {
        if (this.balance > 0) {
            payout();
        } else {
            revert();
        }
    }

    function payout()
        public returns (bool)
    {
        require(getNow() < lockedUntil);
        recipient.transfer(this.balance);
        return true;
    }

    function getNow()
        internal view returns (uint)
    {
        return block.number;
    }

}