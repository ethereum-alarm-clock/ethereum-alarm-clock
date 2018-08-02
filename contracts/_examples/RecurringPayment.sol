pragma solidity 0.4.24;

import "contracts/Interface/SchedulerInterface.sol";

/// Example of using the Scheduler from a smart contract to delay a payment.
contract RecurringPayment {
    SchedulerInterface public scheduler;
    
    uint paymentInterval;
    uint paymentValue;
    uint lockedUntil;

    address recipient;
    address public currentScheduledTransaction;

    event PaymentScheduled(address indexed scheduledTransaction, address recipient, uint value);
    event PaymentExecuted(address indexed scheduledTransaction, address recipient, uint value);

    function RecurringPayment(
        address _scheduler,
        uint _paymentInterval,
        uint _paymentValue,
        address _recipient
    )  public payable {
        scheduler = SchedulerInterface(_scheduler);
        paymentInterval = _paymentInterval;
        recipient = _recipient;
        paymentValue = _paymentValue;

        schedule();
    }

    function ()
        public payable 
    {
        if (msg.value > 0) { //this handles recieving remaining funds sent while scheduling (0.1 ether)
            return;
        } 
        
        process();
    }

    function process() public returns (bool) {
        payout();
        schedule();
    }

    function payout()
        private returns (bool)
    {
        require(block.number >= lockedUntil);
        require(address(this).balance >= paymentValue);
        
        recipient.transfer(paymentValue);

        emit PaymentExecuted(currentScheduledTransaction, recipient, paymentValue);
        return true;
    }

    function schedule() 
        private returns (bool)
    {
        lockedUntil = block.number + paymentInterval;

        currentScheduledTransaction = scheduler.schedule.value(0.1 ether)( // 0.1 ether is to pay for gas, bounty and fee
            this,                   // send to self
            "",                     // and trigger fallback function
            [
                1000000,            // The amount of gas to be sent with the transaction. Accounts for payout + new contract deployment
                0,                  // The amount of wei to be sent.
                255,                // The size of the execution window.
                lockedUntil,        // The start of the execution window.
                20000000000 wei,    // The gasprice for the transaction (aka 20 gwei)
                20000000000 wei,    // The fee included in the transaction.
                20000000000 wei,         // The bounty that awards the executor of the transaction.
                30000000000 wei     // The required amount of wei the claimer must send as deposit.
            ]
        );

        emit PaymentScheduled(currentScheduledTransaction, recipient, paymentValue);
    }
}