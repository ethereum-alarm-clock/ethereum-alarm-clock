pragma solidity ^0.4.21;

import "contracts/Interface/RequestFactoryInterface.sol";

import "contracts/Library/PaymentLib.sol";
import "contracts/Library/RequestLib.sol";
import "contracts/Library/RequestScheduleLib.sol";

import "contracts/Library/MathLib.sol";
import "contracts/zeppelin/SafeMath.sol";

library SchedulerLib {
    using SafeMath for uint;

    struct FutureTransaction {
        address toAddress;          // Destination of the transaction.
        bytes callData;             // Bytecode to be included with the transaction.
        
        uint callGas;               // Amount of gas to be used with the transaction.
        uint callValue;             // Amount of ether to send with the transaction.

        uint windowSize;            // The size of the execution window.
        uint windowStart;           // Block or timestamp for when the window starts.

        uint gasPrice;              // The gasPrice to be sent with the transaction.
        
        uint fee;                   // Fee value attached to the transaction.
        uint bounty;                // Bounty value attached to the transaction.

        uint requiredDeposit;       // The deposit required to claim the transaction.

        uint reservedWindowSize;    // The size of the window in which claimer has exclusive rights to execute.
        uint freezePeriod;          // The size of the window in which nothing happens... Is before execution
        uint claimWindowSize;       // The size of the window in which someone can claim the txRequest

        RequestScheduleLib.TemporalUnit temporalUnit;
    }

    /*
     * @dev Set common default values.
     */
    function resetCommon(FutureTransaction storage self) 
        public returns (bool complete)
    {
        uint defaultBounty = tx.gasprice.mul(1000000);
        if (self.bounty != defaultBounty) {
            self.bounty = defaultBounty;
        }

        uint defaultFee = self.bounty.div(100);
        if (self.fee != defaultFee ) {
            self.fee = defaultFee;
        }

        uint defaultDeposit = self.bounty.mul(2);
        if (self.requiredDeposit != defaultDeposit) {
            self.requiredDeposit = defaultDeposit;
        }

        if (self.toAddress != msg.sender) {
            self.toAddress = msg.sender;
        }
        if (self.callGas != 90000) {
            self.callGas = 90000;
        }
        if (self.callData.length != 0) {
            self.callData = "";
        }
        if (self.gasPrice != 100) {
            self.gasPrice = 100;
        }

        complete = true;
    }

    /*
     * @dev Set default values for block based scheduling.
     */
    function resetAsBlock(FutureTransaction storage self)
        public returns (bool complete)
    {
        require(resetCommon(self));

        if (self.windowSize != 255) {
            self.windowSize = 255;
        }
        if (self.windowStart != block.number + 10) {
            self.windowStart = block.number + 10;
        }
        if (self.reservedWindowSize != 16) {
            self.reservedWindowSize = 16;
        }
        if (self.freezePeriod != 10) {
            self.freezePeriod = 10;
        }
        if (self.claimWindowSize != 255) {
            self.claimWindowSize = 255;
        }

        complete = true;
    }

    /*
     * Set default values for timestamp based scheduling.
     */
    function resetAsTimestamp(FutureTransaction storage self)
        public returns (bool complete)
    {
        require(resetCommon(self));

        if (self.windowSize != 60 minutes) {
            self.windowSize = 60 minutes;
        }
        if (self.windowStart != now + 5 minutes) {
            self.windowStart = now + 5 minutes;
        }
        if (self.reservedWindowSize != 5 minutes) {
            self.reservedWindowSize = 5 minutes;
        }
        if (self.freezePeriod != 3 minutes) {
            self.freezePeriod = 3 minutes;
        }
        if (self.claimWindowSize != 60 minutes) {
            self.claimWindowSize = 60 minutes;
        }

        complete = true;
    }

    /**
     * @dev The lower level interface for creating a transaction request.
     * @param self The FutureTransaction object created in schedule transaction calls.
     * @param _factoryAddress The address of the RequestFactory which creates TransactionRequests.
     * @return The address of a new TransactionRequest.
     */
    function schedule(
        FutureTransaction storage self,
        address _factoryAddress,
        address _feeRecipient
    ) 
        internal returns (address newRequestAddress) 
    {
        RequestFactoryInterface factory = RequestFactoryInterface(_factoryAddress);

        uint endowment = MathLib.min(
            PaymentLib.computeEndowment(
                self.bounty,
                self.fee,
                self.callGas,
                self.callValue,
                self.gasPrice,
                RequestLib.EXECUTION_GAS_OVERHEAD() //180000, line 459 RequestLib
        ), this.balance);

        newRequestAddress = factory.createValidatedRequest.value(endowment)(
            [
                msg.sender,                 // meta.owner
                _feeRecipient,              // paymentData.feeRecipient
                self.toAddress              // txnData.toAddress
            ],
            [
                self.fee,                   // paymentData.fee
                self.bounty,                // paymentData.bounty
                self.claimWindowSize,       // scheduler.claimWindowSize
                self.freezePeriod,          // scheduler.freezePeriod
                self.reservedWindowSize,    // scheduler.reservedWindowSize
                uint(self.temporalUnit),    // scheduler.temporalUnit (1: block, 2: timestamp)
                self.windowSize,            // scheduler.windowSize
                self.windowStart,           // scheduler.windowStart
                self.callGas,               // txnData.callGas
                self.callValue,             // txnData.callValue
                self.gasPrice,              // txnData.gasPrice
                self.requiredDeposit        // claimData.requiredDeposit
            ],
            self.callData
        );
        
        // This check is redundant. see line 55 in BaseScheduler.sol
        // I'm keeping it for now just to cover my bases, even if I'm covering them twice.
        require(newRequestAddress != 0x0);
        return newRequestAddress;
    }

}
