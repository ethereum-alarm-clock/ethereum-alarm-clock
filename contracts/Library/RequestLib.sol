pragma solidity ^0.4.18;

import "contracts/Library/ClaimLib.sol";
import "contracts/Library/ExecutionLib.sol";
import "contracts/Library/PaymentLib.sol";
import "contracts/Library/RequestMetaLib.sol";
import "contracts/Library/RequestScheduleLib.sol";

import "contracts/Library/MathLib.sol";
import "contracts/zeppelin/SafeMath.sol";

library RequestLib {
    using ClaimLib for ClaimLib.ClaimData;
    using ExecutionLib for ExecutionLib.ExecutionData;
    using PaymentLib for PaymentLib.PaymentData;
    using RequestMetaLib for RequestMetaLib.RequestMeta;
    using RequestScheduleLib for RequestScheduleLib.ExecutionWindow;
    using SafeMath for uint;

    /*
     *  This struct exists to circumvent an issue with returning multiple
     *  values from a library function.  I found through experimentation that I
     *  could not return more than 4 things from a library function, even if I
     *  put them in arrays. - Piper
     */
    struct SerializedRequest {
        address[6]  addressValues;
        bool[3]     boolValues;
        uint[15]    uintValues;
        uint8[1]    uint8Values;
    }

    struct Request {
        ExecutionLib.ExecutionData          txnData;
        RequestMetaLib.RequestMeta          meta;
        PaymentLib.PaymentData              paymentData;
        ClaimLib.ClaimData                  claimData;
        RequestScheduleLib.ExecutionWindow  schedule;
        SerializedRequest                   serializedValues;
    }

    enum AbortReason {
        WasCancelled,       //0
        AlreadyCalled,      //1
        BeforeCallWindow,   //2
        AfterCallWindow,    //3
        ReservedForClaimer, //4
        InsufficientGas,    //5
        MismatchGasPrice    //6
    }

    event Aborted(uint8 reason);
    event Cancelled(uint rewardPayment, uint measuredGasConsumption);
    event Claimed();
    event Executed(uint payment, uint fee, uint measuredGasConsumption);

    /**
     * @dev Validate the initialization parameters of a transaction request.
     */
    function validate(
        address[4]  _addressArgs,
        uint[12]    _uintArgs,
        bytes       _callData,
        uint        _endowment
    ) 
        public view returns (bool[6] isValid)
    {
        Request memory request;

        // callData is special.
        request.txnData.callData = _callData;

        // Address values
        request.claimData.claimedBy =               0x0;
        request.meta.createdBy =                    _addressArgs[0];
        request.meta.owner =                        _addressArgs[1];
        request.paymentData.feeRecipient =          _addressArgs[2];
        request.paymentData.paymentBenefactor =     0x0;
        request.txnData.toAddress =                 _addressArgs[3];

        // Boolean values
        request.meta.isCancelled =      false;
        request.meta.wasCalled =        false;
        request.meta.wasSuccessful =    false;

        // UInt values
        request.claimData.claimDeposit =        0;
        request.paymentData.fee =               _uintArgs[0];
        request.paymentData.payment =           _uintArgs[1];
        request.paymentData.feeOwed =           0;
        request.paymentData.paymentOwed =       0;
        request.schedule.claimWindowSize =      _uintArgs[2];
        request.schedule.freezePeriod =         _uintArgs[3];
        request.schedule.reservedWindowSize =   _uintArgs[4];
        // This must be capped at 1 or it throws an exception.
        request.schedule.temporalUnit =         RequestScheduleLib.TemporalUnit(MathLib.min(_uintArgs[5], 2));
        request.schedule.windowSize =           _uintArgs[6];
        request.schedule.windowStart =          _uintArgs[7];
        request.txnData.callGas =               _uintArgs[8];
        request.txnData.callValue =             _uintArgs[9];
        request.txnData.gasPrice =              _uintArgs[10];
        request.claimData.requiredDeposit =     _uintArgs[11];

        // Uint8 values
        request.claimData.paymentModifier = 0;

        // The order of these errors matters as it determines which
        // ValidationError event codes are logged when validation fails.
        isValid[0] = PaymentLib.validateEndowment(
            _endowment,
            request.paymentData.payment,
            request.paymentData.fee,
            request.txnData.callGas,
            request.txnData.callValue,
            request.txnData.gasPrice,
            _EXECUTION_GAS_OVERHEAD
        );
        isValid[1] = RequestScheduleLib.validateReservedWindowSize(
            request.schedule.reservedWindowSize,
            request.schedule.windowSize
        );
        isValid[2] = RequestScheduleLib.validateTemporalUnit(_uintArgs[5]);
        isValid[3] = RequestScheduleLib.validateWindowStart(
            request.schedule.temporalUnit,
            request.schedule.freezePeriod,
            request.schedule.windowStart
        );
        isValid[4] = ExecutionLib.validateCallGas(
            request.txnData.callGas,
            _EXECUTION_GAS_OVERHEAD
        );
        isValid[5] = ExecutionLib.validateToAddress(request.txnData.toAddress);

        return isValid;
    }

    /**
     * @dev Initialize a new Request.
     */
    function initialize(
        Request storage self,
        address[4]      _addressArgs,
        uint[12]        _uintArgs,
        bytes           _callData
    ) 
        public returns (bool initialized)
    {
        address[6] memory addressValues = [
            0x0,                // self.claimData.claimedBy
            _addressArgs[0],    // self.meta.createdBy
            _addressArgs[1],    // self.meta.owner
            _addressArgs[2],    // self.paymentData.feeRecipient
            0x0,                // self.paymentData.paymentBenefactor
            _addressArgs[3]     // self.txnData.toAddress
        ];

        bool[3] memory boolValues = [false, false, false];

        uint[15] memory uintValues = [
            0,                  // self.claimData.claimDeposit
            _uintArgs[0],       // self.paymentData.fee
            0,                  // self.paymentData.feeOwed
            _uintArgs[1],       // self.paymentData.payment
            0,                  // self.paymentData.paymentOwed
            _uintArgs[2],       // self.schedule.claimWindowSize
            _uintArgs[3],       // self.schedule.freezePeriod
            _uintArgs[4],       // self.schedule.reservedWindowSize
            _uintArgs[5],       // self.schedule.temporalUnit
            _uintArgs[6],       // self.schedule.windowSize
            _uintArgs[7],       // self.schedule.windowStart
            _uintArgs[8],       // self.txnData.callGas
            _uintArgs[9],       // self.txnData.callValue
            _uintArgs[10],      // self.txnData.gasPrice
            _uintArgs[11]       // self.claimData.requiredDeposit
        ];

        uint8[1] memory uint8Values = [
            0
        ];

        require( deserialize(self, addressValues, boolValues, uintValues, uint8Values, _callData) );

        return true;
    }

    /*
     *  Returns the entire data structure of the Request in a *serialized*
     *  format.  This will be missing the `callData` which must be requested
     *  separately
     *
     *  Parameter order is alphabetical by type, then namespace, then name
     *
     *  NOTE: This exists because of an issue I ran into related to returning
     *  multiple values from a library function.  I found through
     *  experimentation that I was unable to return more than 4 things, even if
     *  I used the trick of returning arrays of items.
     */
    function serialize(Request storage self) 
        internal returns (bool serialized)
    {
        // Address values
        self.serializedValues.addressValues[0] = self.claimData.claimedBy;
        self.serializedValues.addressValues[1] = self.meta.createdBy;
        self.serializedValues.addressValues[2] = self.meta.owner;
        self.serializedValues.addressValues[3] = self.paymentData.feeRecipient;
        self.serializedValues.addressValues[4] = self.paymentData.paymentBenefactor;
        self.serializedValues.addressValues[5] = self.txnData.toAddress;

        // Boolean values
        self.serializedValues.boolValues[0] = self.meta.isCancelled;
        self.serializedValues.boolValues[1] = self.meta.wasCalled;
        self.serializedValues.boolValues[2] = self.meta.wasSuccessful;

        // UInt256 values
        self.serializedValues.uintValues[0] = self.claimData.claimDeposit;
        self.serializedValues.uintValues[1] = self.paymentData.fee;
        self.serializedValues.uintValues[2] = self.paymentData.feeOwed;
        self.serializedValues.uintValues[3] = self.paymentData.payment;
        self.serializedValues.uintValues[4] = self.paymentData.paymentOwed;
        self.serializedValues.uintValues[5] = self.schedule.claimWindowSize;
        self.serializedValues.uintValues[6] = self.schedule.freezePeriod;
        self.serializedValues.uintValues[7] = self.schedule.reservedWindowSize;
        self.serializedValues.uintValues[8] = uint(self.schedule.temporalUnit);
        self.serializedValues.uintValues[9] = self.schedule.windowSize;
        self.serializedValues.uintValues[10] = self.schedule.windowStart;
        self.serializedValues.uintValues[11] = self.txnData.callGas;
        self.serializedValues.uintValues[12] = self.txnData.callValue;
        self.serializedValues.uintValues[13] = self.txnData.gasPrice;
        self.serializedValues.uintValues[14] = self.claimData.requiredDeposit;

        // Uint8 values
        self.serializedValues.uint8Values[0] = self.claimData.paymentModifier;

        return true;
    }

    /**
     * @dev Populates a Request object from the full output of `serialize`.
     *
     *  Parameter order is alphabetical by type, then namespace, then name.
     */
    function deserialize(
        Request storage self,
        address[6]  _addressValues,
        bool[3]     _boolValues,
        uint[15]    _uintValues,
        uint8[1]    _uint8Values,
        bytes       _callData
    )
        internal returns (bool deserialized)
    {
        // callData is special.
        self.txnData.callData = _callData;

        // Address values
        self.claimData.claimedBy =              _addressValues[0];
        self.meta.createdBy =                   _addressValues[1];
        self.meta.owner =                       _addressValues[2];
        self.paymentData.feeRecipient =         _addressValues[3];
        self.paymentData.paymentBenefactor =    _addressValues[4];
        self.txnData.toAddress =                _addressValues[5];

        // Boolean values
        self.meta.isCancelled =     _boolValues[0];
        self.meta.wasCalled =       _boolValues[1];
        self.meta.wasSuccessful =   _boolValues[2];

        // UInt values
        self.claimData.claimDeposit =       _uintValues[0];
        self.paymentData.fee =              _uintValues[1];
        self.paymentData.feeOwed =          _uintValues[2];
        self.paymentData.payment =          _uintValues[3];
        self.paymentData.paymentOwed =      _uintValues[4];
        self.schedule.claimWindowSize =     _uintValues[5];
        self.schedule.freezePeriod =        _uintValues[6];
        self.schedule.reservedWindowSize =  _uintValues[7];
        self.schedule.temporalUnit =        RequestScheduleLib.TemporalUnit(_uintValues[8]);
        self.schedule.windowSize =          _uintValues[9];
        self.schedule.windowStart =         _uintValues[10];
        self.txnData.callGas =              _uintValues[11];
        self.txnData.callValue =            _uintValues[12];
        self.txnData.gasPrice =             _uintValues[13];
        self.claimData.requiredDeposit =    _uintValues[14];

        // Uint8 values
        self.claimData.paymentModifier = _uint8Values[0];

        deserialized = true;
    }

    function execute(Request storage self) 
        internal returns (bool)
    {
        /*
         *  Execute the TransactionRequest
         *
         *  +---------------------+
         *  | Phase 1: Validation |
         *  +---------------------+
         *
         *  Must pass all of the following checks:
         *
         *  1. Not already called.
         *  2. Not cancelled.
         *  3. Not before the execution window.
         *  4. Not after the execution window.
         *  5. if (claimedBy == 0x0 or msg.sender == claimedBy):
         *         - windowStart <= block.number
         *         - block.number <= windowStart + windowSize
         *     else if (msg.sender != claimedBy):
         *         - windowStart + reservedWindowSize <= block.number
         *         - block.number <= windowStart + windowSize
         *     else:
         *         - throw (should be impossible)
         *  
         *  6. msg.gas == callGas
         *
         *  +--------------------+
         *  | Phase 2: Execution |
         *  +--------------------+
         *
         *  1. Mark as called (must be before actual execution to prevent
         *     re-entrance)
         *  2. Send Transaction and record success or failure.
         *
         *  +---------------------+
         *  | Phase 3: Accounting |
         *  +---------------------+
         *
         *  1. Calculate and send fee amount.
         *  2. Calculate and send payment amount.
         *  3. Send remaining ether back to owner.
         *
         */

        uint startGas = msg.gas;

        // +----------------------+
        // | Begin: Authorization |
        // +----------------------+

        if (msg.gas < requiredExecutionGas(self).sub(_PRE_EXECUTION_GAS)) {
            Aborted(uint8(AbortReason.InsufficientGas));
            return false;
        } else if (self.meta.wasCalled) {
            Aborted(uint8(AbortReason.AlreadyCalled));
            return false;
        } else if (self.meta.isCancelled) {
            Aborted(uint8(AbortReason.WasCancelled));
            return false;
        } else if (self.schedule.isBeforeWindow()) {
            Aborted(uint8(AbortReason.BeforeCallWindow));
            return false;
        } else if (self.schedule.isAfterWindow()) {
            Aborted(uint8(AbortReason.AfterCallWindow));
            return false;
        } else if (self.claimData.isClaimed() &&
                   msg.sender != self.claimData.claimedBy &&
                   self.schedule.inReservedWindow()) {
            Aborted(uint8(AbortReason.ReservedForClaimer));
            return false;
        } else if (self.txnData.gasPrice != tx.gasprice) {
            Aborted(uint8(AbortReason.MismatchGasPrice));
            return false;
        }

        // +--------------------+
        // | End: Authorization |
        // +--------------------+
        // +------------------+
        // | Begin: Execution |
        // +------------------+

        /// Mark as being called before sending transaction to prevent re-entrance.
        self.meta.wasCalled = true;

        /// Send the transaction...
        /// The transaction is allowed to fail and the caller will still get paid.
        self.meta.wasSuccessful = self.txnData.sendTransaction();

        // +----------------+
        // | End: Execution |
        // +----------------+
        // +-------------------+
        // | Begin: Accounting |
        // +-------------------+

        // Compute the fee amount
        if (self.paymentData.hasBenefactor()) {
            self.paymentData.feeOwed = self.paymentData.getFee()
                                        .add(self.paymentData.feeOwed);
        }

        // record this so that we can log it later.
        uint totalFeePayment = self.paymentData.feeOwed;

        // Send the fee.
        self.paymentData.sendFee();

        // Compute the payment amount and who it should be sent do.
        self.paymentData.paymentBenefactor = msg.sender;
        if (self.claimData.isClaimed()) {
            self.paymentData.paymentOwed = self.claimData.claimDeposit.add(self.paymentData.paymentOwed);
            // need to zero out the claim deposit since it is now accounted for
            // in the paymentOwed value.
            self.claimData.claimDeposit = 0;
            self.paymentData.paymentOwed = self.paymentData.getPaymentWithModifier(self.claimData.paymentModifier)
                                                           .add(self.paymentData.paymentOwed);
        } else {
            self.paymentData.paymentOwed = self.paymentData.getPayment()
                                                           .add(self.paymentData.paymentOwed);
        }

        // Record the amount of gas used by execution.
        uint measuredGasConsumption = startGas.sub(msg.gas).add(_EXECUTE_EXTRA_GAS);

        // // +----------------------------------------------------------------------+
        // // | NOTE: All code after this must be accounted for by EXECUTE_EXTRA_GAS |
        // // +----------------------------------------------------------------------+

        // Add the gas reimbursment amount to the payment.
        self.paymentData.paymentOwed = measuredGasConsumption.mul(tx.gasprice)
                                                             .add(self.paymentData.paymentOwed);

        // Log the two payment amounts.  Otherwise it is non-trivial to figure
        // out how much was payed.
        Executed(self.paymentData.paymentOwed,
                 totalFeePayment,
                 measuredGasConsumption);
    
        // Attempt to send the payment. This is allowed to fail so it may need to be called again.
        self.paymentData.sendPayment();

        // Send all extra ether back to the owner.
        _sendOwnerEther(self);

        // +-----------------+
        // | End: Accounting |
        // +-----------------+
        return true;
    }


    // This is the amount of gas that it takes to enter from the
    // `TransactionRequest.execute()` contract into the `RequestLib.execute()`
    // method at the point where the gas check happens.
    uint private constant _PRE_EXECUTION_GAS = 25000;   // TODO is this number still accurate?

    function PRE_EXECUTION_GAS()
        public pure returns (uint)
    {
        return _PRE_EXECUTION_GAS;
    }

    function requiredExecutionGas(Request storage self) 
        public view returns (uint requiredGas)
    {
        requiredGas = self.txnData.callGas.add(_EXECUTION_GAS_OVERHEAD);
    }

    /*
     * The amount of gas needed to complete the execute method after
     * the transaction has been sent.
     */
    uint private constant _EXECUTION_GAS_OVERHEAD = 180000; // TODO check accuracy of this number

    function EXECUTION_GAS_OVERHEAD()
        public pure returns (uint)
    {
        return _EXECUTION_GAS_OVERHEAD;
    }

    
    /*
     *  The amount of gas used by the portion of the `execute` function
     *  that cannot be accounted for via gas tracking.
     */
    uint private constant  _EXECUTE_EXTRA_GAS = 90000; // again, check for accuracy... Doubled this from Piper's original - Logan

    function EXECUTE_EXTRA_GAS() 
        public pure returns (uint)
    {
        return _EXECUTE_EXTRA_GAS;
    }

    /*
     * @dev Performs the checks to see if a request can be cancelled.
     *  Must satisfy the following conditions.
     *
     *  1. Not Cancelled
     *  2. either:
     *    * not wasCalled && afterExecutionWindow
     *    * not claimed && beforeFreezeWindow && msg.sender == owner
     */
    function isCancellable(Request storage self) 
        internal view returns (bool)
    {
        if (self.meta.isCancelled) {
            // already cancelled!
            return false;
        } else if (!self.meta.wasCalled && self.schedule.isAfterWindow()) {
            // not called but after the window
            return true;
        } else if (!self.claimData.isClaimed() && self.schedule.isBeforeFreeze() && msg.sender == self.meta.owner) {
            // not claimed and before freezePeriod and owner is cancelling
            return true;
        } else {
            // otherwise cannot cancel
            return false;
        }
    }

    /*
     *  Constant value to account for the gas usage that cannot be accounted
     *  for using gas-tracking within the `cancel` function.
     */
    uint private constant _CANCEL_EXTRA_GAS = 85000; // Check accuracy

    function CANCEL_EXTRA_GAS() 
        public pure returns (uint)
    {
        return _CANCEL_EXTRA_GAS;
    }

    /*
     *  Cancel the transaction request, attempting to send all appropriate
     *  refunds.  To incentivise cancellation by other parties, a small reward
     *  payment is issued to the party that cancels the request if they are not
     *  the owner.
     */
    function cancel(Request storage self) 
        public returns (bool)
    {
        uint startGas = msg.gas;
        uint rewardPayment;
        uint measuredGasConsumption;

        /// Checks if this transactionRequest can be cancelled.
        require( isCancellable(self) );

        /// Set here to prevent re-entrance attacks.
        self.meta.isCancelled = true;

        /// Refund the claim deposit (if there is one)
        require( self.claimData.refundDeposit() );

        /// Send a reward to the canceller if they are not the owner.
        /// This is to incentivize the cancelling of expired transactionRequests.
        // This also guarantees that it is being cancelled after the call window
        // since the `isCancellable()` function checks this.
        if (msg.sender != self.meta.owner) {
            /// Create the rewardBenefactor
            address rewardBenefactor = msg.sender;
            /// Create the rewardOwed variable, it is one-hundredth
            /// of the payment.
            uint rewardOwed = self.paymentData.paymentOwed.add(
                self.paymentData.payment.div(100)
            );

            /// Calc the amount of gas caller used to call this function.
            measuredGasConsumption = startGas.sub(msg.gas).add(_CANCEL_EXTRA_GAS);
            /// Add their gas fees to the reward.
            rewardOwed = measuredGasConsumption.mul(tx.gasprice).add(rewardOwed);

            /// Take note of the rewardPayment to log it.
            rewardPayment = rewardOwed;

            /// Transfers the rewardPayment.
            if (rewardOwed > 0) {
                self.paymentData.paymentOwed = 0;
                rewardBenefactor.transfer(rewardOwed);
            }
        }

        /// Logs are our friends.
        Cancelled(rewardPayment, measuredGasConsumption);

        // send the remaining ether to the owner.
        return sendOwnerEther(self);
        // return true;
    }

    /*
     * @dev Performs the checks to verify that a request is claimable.
     * @param self The Request object.
     */
    function isClaimable(Request storage self) 
        internal view returns (bool)
    {
        /// Require not claimed and not cancelled.
        require( !self.claimData.isClaimed() );
        require( !self.meta.isCancelled );

        // Require that it's in the claim window and the value sent is over the min deposit.
        require( self.schedule.inClaimWindow() );
        require( msg.value >= self.claimData.requiredDeposit );
        return true;
    }

    /*
     * @dev Claims the request.
     * @param self The Request object.
     * Payable because it requires the sender to send enough ether to cover the claimDeposit.
     */
    function claim(Request storage self) 
        internal returns (bool claimed)
    {
        require( isClaimable(self) );

        self.claimData.claim(self.schedule.computePaymentModifier());
        Claimed();
        claimed = true;
    }

    /*
     * @dev Refund claimer deposit.
     */
    function refundClaimDeposit(Request storage self)
        public returns (bool)
    {
        require( self.meta.isCancelled || self.schedule.isAfterWindow() );
        return self.claimData.refundDeposit();
    }

    /*
     * Send fee
     */
    function sendFee(Request storage self) 
        public returns (bool)
    {
        if (self.schedule.isAfterWindow()) {
            return self.paymentData.sendFee();
        }
        return false;
    }

    /*
     * Send payment
     */
    function sendPayment(Request storage self) 
        public returns (bool)
    {
        /// check wasCalled
        if (self.schedule.isAfterWindow()) {
            return self.paymentData.sendPayment();
        }
        return false;
    }

    function sendOwnerEther(Request storage self)
        public returns (bool)
    {
        if( self.meta.isCancelled || self.schedule.isAfterWindow() ) {
            return _sendOwnerEther(self);
        }
        return false;
    }

    function _sendOwnerEther(Request storage self) 
        internal returns (bool)
    {
        // Note! This does not do any checks since it is used in the execute function.
        // The public version of the function should be used for checks and in the cancel function.
        uint ownerRefund = this.balance.sub(self.claimData.claimDeposit)
                                .sub(self.paymentData.paymentOwed)
                                .sub(self.paymentData.feeOwed);
        return self.meta.owner.send(ownerRefund);
    }
}
