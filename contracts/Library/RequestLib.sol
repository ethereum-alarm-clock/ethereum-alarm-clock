pragma solidity 0.4.24;

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

    struct Request {
        ExecutionLib.ExecutionData txnData;
        RequestMetaLib.RequestMeta meta;
        PaymentLib.PaymentData paymentData;
        ClaimLib.ClaimData claimData;
        RequestScheduleLib.ExecutionWindow schedule;
    }

    enum AbortReason {
        WasCancelled,       //0
        AlreadyCalled,      //1
        BeforeCallWindow,   //2
        AfterCallWindow,    //3
        ReservedForClaimer, //4
        InsufficientGas,    //5
        TooLowGasPrice    //6
    }

    event Aborted(uint8 reason);
    event Cancelled(uint rewardPayment, uint measuredGasConsumption);
    event Claimed();
    event Executed(uint bounty, uint fee, uint measuredGasConsumption);

    /**
     * @dev Validate the initialization parameters of a transaction request.
     */
    function validate(
        address[4]  _addressArgs,
        uint[12]    _uintArgs,
        uint        _endowment
    ) 
        public view returns (bool[6] isValid)
    {
        // The order of these errors matters as it determines which
        // ValidationError event codes are logged when validation fails.
        isValid[0] = PaymentLib.validateEndowment(
            _endowment,
            _uintArgs[1],               //bounty
            _uintArgs[0],               //fee
            _uintArgs[8],               //callGas
            _uintArgs[9],               //callValue
            _uintArgs[10],              //gasPrice
            EXECUTION_GAS_OVERHEAD
        );
        isValid[1] = RequestScheduleLib.validateReservedWindowSize(
            _uintArgs[4],               //reservedWindowSize
            _uintArgs[6]                //windowSize
        );
        isValid[2] = RequestScheduleLib.validateTemporalUnit(_uintArgs[5]);
        isValid[3] = RequestScheduleLib.validateWindowStart(
            RequestScheduleLib.TemporalUnit(MathLib.min(_uintArgs[5], 2)),
            _uintArgs[3],               //freezePeriod
            _uintArgs[7]                //windowStart
        );
        isValid[4] = ExecutionLib.validateCallGas(
            _uintArgs[8],               //callGas
            EXECUTION_GAS_OVERHEAD
        );
        isValid[5] = ExecutionLib.validateToAddress(_addressArgs[3]);

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
        public returns (bool)
    {
        address[6] memory addressValues = [
            0x0,                // self.claimData.claimedBy
            _addressArgs[0],    // self.meta.createdBy
            _addressArgs[1],    // self.meta.owner
            _addressArgs[2],    // self.paymentData.feeRecipient
            0x0,                // self.paymentData.bountyBenefactor
            _addressArgs[3]     // self.txnData.toAddress
        ];

        bool[3] memory boolValues = [false, false, false];

        uint[15] memory uintValues = [
            0,                  // self.claimData.claimDeposit
            _uintArgs[0],       // self.paymentData.fee
            0,                  // self.paymentData.feeOwed
            _uintArgs[1],       // self.paymentData.bounty
            0,                  // self.paymentData.bountyOwed
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

        require(deserialize(self, addressValues, boolValues, uintValues, uint8Values, _callData));

        return true;
    }
 
    function serialize(Request storage self)
        internal view returns(address[6], bool[3], uint[15], uint8[1])
    {
        address[6] memory addressValues = [
            self.claimData.claimedBy,
            self.meta.createdBy,
            self.meta.owner,
            self.paymentData.feeRecipient,
            self.paymentData.bountyBenefactor,
            self.txnData.toAddress
        ];

        bool[3] memory boolValues = [
            self.meta.isCancelled,
            self.meta.wasCalled,
            self.meta.wasSuccessful
        ];

        uint[15] memory uintValues = [
            self.claimData.claimDeposit,
            self.paymentData.fee,
            self.paymentData.feeOwed,
            self.paymentData.bounty,
            self.paymentData.bountyOwed,
            self.schedule.claimWindowSize,
            self.schedule.freezePeriod,
            self.schedule.reservedWindowSize,
            uint(self.schedule.temporalUnit),
            self.schedule.windowSize,
            self.schedule.windowStart,
            self.txnData.callGas,
            self.txnData.callValue,
            self.txnData.gasPrice,
            self.claimData.requiredDeposit
        ];

        uint8[1] memory uint8Values = [
            self.claimData.paymentModifier
        ];

        return (addressValues, boolValues, uintValues, uint8Values);
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
        internal returns (bool)
    {
        // callData is special.
        self.txnData.callData = _callData;

        // Address values
        self.claimData.claimedBy = _addressValues[0];
        self.meta.createdBy = _addressValues[1];
        self.meta.owner = _addressValues[2];
        self.paymentData.feeRecipient = _addressValues[3];
        self.paymentData.bountyBenefactor = _addressValues[4];
        self.txnData.toAddress = _addressValues[5];

        // Boolean values
        self.meta.isCancelled = _boolValues[0];
        self.meta.wasCalled = _boolValues[1];
        self.meta.wasSuccessful = _boolValues[2];

        // UInt values
        self.claimData.claimDeposit = _uintValues[0];
        self.paymentData.fee = _uintValues[1];
        self.paymentData.feeOwed = _uintValues[2];
        self.paymentData.bounty = _uintValues[3];
        self.paymentData.bountyOwed = _uintValues[4];
        self.schedule.claimWindowSize = _uintValues[5];
        self.schedule.freezePeriod = _uintValues[6];
        self.schedule.reservedWindowSize = _uintValues[7];
        self.schedule.temporalUnit = RequestScheduleLib.TemporalUnit(_uintValues[8]);
        self.schedule.windowSize = _uintValues[9];
        self.schedule.windowStart = _uintValues[10];
        self.txnData.callGas = _uintValues[11];
        self.txnData.callValue = _uintValues[12];
        self.txnData.gasPrice = _uintValues[13];
        self.claimData.requiredDeposit = _uintValues[14];

        // Uint8 values
        self.claimData.paymentModifier = _uint8Values[0];

        return true;
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
         *  6. gasleft() == callGas
         *  7. tx.gasprice >= txnData.gasPrice
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
         *  2. Calculate and send bounty amount.
         *  3. Send remaining ether back to owner.
         *
         */

        // Record the gas at the beginning of the transaction so we can
        // calculate how much has been used later.
        uint startGas = gasleft();

        // +----------------------+
        // | Begin: Authorization |
        // +----------------------+

        if (gasleft() < requiredExecutionGas(self).sub(PRE_EXECUTION_GAS)) {
            emit Aborted(uint8(AbortReason.InsufficientGas));
            return false;
        } else if (self.meta.wasCalled) {
            emit Aborted(uint8(AbortReason.AlreadyCalled));
            return false;
        } else if (self.meta.isCancelled) {
            emit Aborted(uint8(AbortReason.WasCancelled));
            return false;
        } else if (self.schedule.isBeforeWindow()) {
            emit Aborted(uint8(AbortReason.BeforeCallWindow));
            return false;
        } else if (self.schedule.isAfterWindow()) {
            emit Aborted(uint8(AbortReason.AfterCallWindow));
            return false;
        } else if (self.claimData.isClaimed() && msg.sender != self.claimData.claimedBy && self.schedule.inReservedWindow()) {
            emit Aborted(uint8(AbortReason.ReservedForClaimer));
            return false;
        } else if (self.txnData.gasPrice > tx.gasprice) {
            emit Aborted(uint8(AbortReason.TooLowGasPrice));
            return false;
        }

        // +--------------------+
        // | End: Authorization |
        // +--------------------+
        // +------------------+
        // | Begin: Execution |
        // +------------------+

        // Mark as being called before sending transaction to prevent re-entrance.
        self.meta.wasCalled = true;

        // Send the transaction...
        // The transaction is allowed to fail and the executing agent will still get the bounty.
        // `.sendTransaction()` will return false on a failed exeuction. 
        self.meta.wasSuccessful = self.txnData.sendTransaction();

        // +----------------+
        // | End: Execution |
        // +----------------+
        // +-------------------+
        // | Begin: Accounting |
        // +-------------------+

        // Compute the fee amount
        if (self.paymentData.hasFeeRecipient()) {
            self.paymentData.feeOwed = self.paymentData.getFee()
                .add(self.paymentData.feeOwed);
        }

        // Record this locally so that we can log it later.
        // `.sendFee()` below will change `self.paymentData.feeOwed` to 0 to prevent re-entrance.
        uint totalFeePayment = self.paymentData.feeOwed;

        // Send the fee. This transaction may also fail but can be called again after
        // execution.
        self.paymentData.sendFee();

        // Compute the bounty amount.
        self.paymentData.bountyBenefactor = msg.sender;
        if (self.claimData.isClaimed()) {
            // If the transaction request was claimed, we add the deposit to the bounty whether
            // or not the same agent who claimed is executing.
            self.paymentData.bountyOwed = self.claimData.claimDeposit
                .add(self.paymentData.bountyOwed);
            // To prevent re-entrance we zero out the claim deposit since it is now accounted for
            // in the bounty value.
            self.claimData.claimDeposit = 0;
            // Depending on when the transaction request was claimed, we apply the modifier to the
            // bounty payment and add it to the bounty already owed.
            self.paymentData.bountyOwed = self.paymentData.getBountyWithModifier(self.claimData.paymentModifier)
                .add(self.paymentData.bountyOwed);
        } else {
            // Not claimed. Just add the full bounty.
            self.paymentData.bountyOwed = self.paymentData.getBounty().add(self.paymentData.bountyOwed);
        }

        // Take down the amount of gas used so far in execution to compensate the executing agent.
        uint measuredGasConsumption = startGas.sub(gasleft()).add(EXECUTE_EXTRA_GAS);

        // // +----------------------------------------------------------------------+
        // // | NOTE: All code after this must be accounted for by EXECUTE_EXTRA_GAS |
        // // +----------------------------------------------------------------------+

        // Add the gas reimbursment amount to the bounty.
        self.paymentData.bountyOwed = measuredGasConsumption
            .mul(self.txnData.gasPrice)
            .add(self.paymentData.bountyOwed);

        // Log the bounty and fee. Otherwise it is non-trivial to figure
        // out how much was payed.
        emit Executed(self.paymentData.bountyOwed, totalFeePayment, measuredGasConsumption);
    
        // Attempt to send the bounty. as with `.sendFee()` it may fail and need to be caled after execution.
        self.paymentData.sendBounty();

        // If any ether is left, send it back to the owner of the transaction request.
        _sendOwnerEther(self, self.meta.owner);

        // +-----------------+
        // | End: Accounting |
        // +-----------------+
        // Successful
        return true;
    }


    // This is the amount of gas that it takes to enter from the
    // `TransactionRequest.execute()` contract into the `RequestLib.execute()`
    // method at the point where the gas check happens.
    uint public constant PRE_EXECUTION_GAS = 25000;   // TODO is this number still accurate?
    
    /*
     * The amount of gas needed to complete the execute method after
     * the transaction has been sent.
     */
    uint public constant EXECUTION_GAS_OVERHEAD = 180000; // TODO check accuracy of this number
    /*
     *  The amount of gas used by the portion of the `execute` function
     *  that cannot be accounted for via gas tracking.
     */
    uint public constant  EXECUTE_EXTRA_GAS = 90000; // again, check for accuracy... Doubled this from Piper's original - Logan

    /*
     *  Constant value to account for the gas usage that cannot be accounted
     *  for using gas-tracking within the `cancel` function.
     */
    uint public constant CANCEL_EXTRA_GAS = 85000; // Check accuracy

    function getEXECUTION_GAS_OVERHEAD()
        public pure returns (uint)
    {
        return EXECUTION_GAS_OVERHEAD;
    }
    
    function requiredExecutionGas(Request storage self) 
        public view returns (uint requiredGas)
    {
        requiredGas = self.txnData.callGas.add(EXECUTION_GAS_OVERHEAD);
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
        public view returns (bool)
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
     *  Cancel the transaction request, attempting to send all appropriate
     *  refunds.  To incentivise cancellation by other parties, a small reward
     *  payment is issued to the party that cancels the request if they are not
     *  the owner.
     */
    function cancel(Request storage self) 
        public returns (bool)
    {
        uint startGas = gasleft();
        uint rewardPayment;
        uint measuredGasConsumption;

        // Checks if this transactionRequest can be cancelled.
        require(isCancellable(self));

        // Set here to prevent re-entrance attacks.
        self.meta.isCancelled = true;

        // Refund the claim deposit (if there is one)
        require(self.claimData.refundDeposit());

        // Send a reward to the cancelling agent if they are not the owner.
        // This is to incentivize the cancelling of expired transaction requests.
        // This also guarantees that it is being cancelled after the call window
        // since the `isCancellable()` function checks this.
        if (msg.sender != self.meta.owner) {
            // Create the rewardBenefactor
            address rewardBenefactor = msg.sender;
            // Create the rewardOwed variable, it is one-hundredth
            // of the bounty.
            uint rewardOwed = self.paymentData.bountyOwed
                .add(self.paymentData.bounty.div(100));

            // Calculate the amount of gas cancelling agent used in this transaction.
            measuredGasConsumption = startGas
                .sub(gasleft())
                .add(CANCEL_EXTRA_GAS);
            // Add their gas fees to the reward.W
            rewardOwed = measuredGasConsumption
                .mul(tx.gasprice)
                .add(rewardOwed);

            // Take note of the rewardPayment to log it.
            rewardPayment = rewardOwed;

            // Transfers the rewardPayment.
            if (rewardOwed > 0) {
                self.paymentData.bountyOwed = 0;
                rewardBenefactor.transfer(rewardOwed);
            }
        }

        // Log it!
        emit Cancelled(rewardPayment, measuredGasConsumption);

        // Send the remaining ether to the owner.
        return sendOwnerEther(self);
    }

    /*
     * @dev Performs some checks to verify that a transaction request is claimable.
     * @param self The Request object.
     */
    function isClaimable(Request storage self) 
        internal view returns (bool)
    {
        // Require not claimed and not cancelled.
        require(!self.claimData.isClaimed());
        require(!self.meta.isCancelled);

        // Require that it's in the claim window and the value sent is over the required deposit.
        require(self.schedule.inClaimWindow());
        require(msg.value >= self.claimData.requiredDeposit);
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
        require(isClaimable(self));
        
        emit Claimed();
        return self.claimData.claim(self.schedule.computePaymentModifier());
    }

    /*
     * @dev Refund claimer deposit.
     */
    function refundClaimDeposit(Request storage self)
        public returns (bool)
    {
        require(self.meta.isCancelled || self.schedule.isAfterWindow());
        return self.claimData.refundDeposit();
    }

    /*
     * Send fee. Wrapper over the real function that perform an extra
     * check to see if it's after the execution window (and thus the first transaction failed)
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
     * Send bounty. Wrapper over the real function that performs an extra
     * check to see if it's after execution window (and thus the first transaction failed)
     */
    function sendBounty(Request storage self) 
        public returns (bool)
    {
        /// check wasCalled
        if (self.schedule.isAfterWindow()) {
            return self.paymentData.sendBounty();
        }
        return false;
    }

    function canSendOwnerEther(Request storage self) 
        public view returns(bool) 
    {
        return self.meta.isCancelled || self.schedule.isAfterWindow() || self.meta.wasCalled;
    }

    /**
     * Send owner ether. Wrapper over the real function that performs an extra 
     * check to see if it's after execution window (and thus the first transaction failed)
     */
    function sendOwnerEther(Request storage self, address recipient)
        public returns (bool)
    {
        require(recipient != 0x0);
        if(canSendOwnerEther(self) && msg.sender == self.meta.owner) {
            return _sendOwnerEther(self, recipient);
        }
        return false;
    }

    /**
     * Send owner ether. Wrapper over the real function that performs an extra 
     * check to see if it's after execution window (and thus the first transaction failed)
     */
    function sendOwnerEther(Request storage self)
        public returns (bool)
    {
        if(canSendOwnerEther(self)) {
            return _sendOwnerEther(self, self.meta.owner);
        }
        return false;
    }

    function _sendOwnerEther(Request storage self, address recipient) 
        private returns (bool)
    {
        // Note! This does not do any checks since it is used in the execute function.
        // The public version of the function should be used for checks and in the cancel function.
        uint ownerRefund = address(this).balance
            .sub(self.claimData.claimDeposit)
            .sub(self.paymentData.bountyOwed)
            .sub(self.paymentData.feeOwed);
        /* solium-disable security/no-send */
        return recipient.send(ownerRefund);
    }
}