//pragma solidity 0.4.1;

import {ExecutionLib} from "contracts/ExecutionLib.sol";
import {RequestScheduleLib} from "contracts/RequestScheduleLib.sol";
import {ClaimLib} from "contracts/ClaimLib.sol";
import {RequestMetaLib} from "contracts/RequestMetaLib.sol";
import {PaymentLib} from "contracts/PaymentLib.sol";
import {SafeSendLib} from "contracts/SafeSendLib.sol";
import {MathLib} from "contracts/MathLib.sol";


library RequestLib {
    using ExecutionLib for ExecutionLib.ExecutionData;
    using RequestScheduleLib for RequestScheduleLib.ExecutionWindow;
    using ClaimLib for ClaimLib.ClaimData;
    using RequestMetaLib for RequestMetaLib.RequestMeta;
    using PaymentLib for PaymentLib.PaymentData;
    using SafeSendLib for address;
    using MathLib for uint;

    struct SerializedRequest {
        address[6] addressValues;
        bool[3] boolValues;
        uint[15] uintValues;
        uint8[1] uint8Values;
    }

    struct Request {
        ExecutionLib.ExecutionData txnData;
        RequestMetaLib.RequestMeta meta;
        PaymentLib.PaymentData paymentData;
        ClaimLib.ClaimData claimData;
        RequestScheduleLib.ExecutionWindow schedule;
        SerializedRequest serializedValues;
    }

    /*
     *  Validate the initialization parameters for a transaction request.
     */
    function validate(address[4] addressArgs,
                      uint[11] uintArgs,
                      bytes callData,
                      uint endowment) returns (bool[7] is_valid) {
        Request memory request;

        // callData is special.
        request.txnData.callData = callData;

        // Address values
        request.claimData.claimedBy = 0x0;
        request.meta.createdBy = addressArgs[0];
        request.meta.owner = addressArgs[1];
        request.paymentData.donationBenefactor = addressArgs[2];
        request.paymentData.donationBenefactor = 0x0;
        request.txnData.toAddress = addressArgs[3];

        // Boolean values
        request.meta.isCancelled = false;
        request.meta.wasCalled = false;
        request.meta.wasSuccessful = false;

        // UInt values
        request.claimData.claimDeposit = 0;
        request.paymentData.anchorGasPrice = tx.gasprice;
        request.paymentData.donation = uintArgs[0];
        request.paymentData.payment = uintArgs[1];
        request.paymentData.donationOwed = 0;
        request.paymentData.paymentOwed = 0;
        request.schedule.claimWindowSize = uintArgs[2];
        request.schedule.freezePeriod = uintArgs[3];
        request.schedule.reservedWindowSize = uintArgs[4];
        // This must be capped at 1 or it throws an exception.
        request.schedule.temporalUnit = RequestScheduleLib.TemporalUnit(uintArgs[5].min(1));
        request.schedule.windowStart = uintArgs[6];
        request.schedule.windowSize = uintArgs[7];
        request.txnData.callGas = uintArgs[8];
        request.txnData.callValue = uintArgs[9];
        request.txnData.requiredStackDepth = uintArgs[10];

        // Uint8 values
        request.claimData.paymentModifier = 0;

        // The order of these errors matters as it determines which
        // ValidationError event codes are logged when validation fails.
        is_valid[0] = PaymentLib.validateEndowment(endowment,
                                                   request.paymentData.payment,
                                                   request.paymentData.donation,
                                                   request.txnData.callGas,
                                                   request.txnData.callValue);
        is_valid[1] = RequestScheduleLib.validateReservedWindowSize(request.schedule.reservedWindowSize,
                                                                    request.schedule.windowSize);
        is_valid[2] = RequestScheduleLib.validateTemporalUnit(uintArgs[5]);
        is_valid[3] = RequestScheduleLib.validateWindowStart(request.schedule.temporalUnit,
                                                             request.schedule.freezePeriod,
                                                             request.schedule.windowStart);
        is_valid[4] = ExecutionLib.validateRequiredStackDepth(request.txnData.requiredStackDepth);
        is_valid[5] = ExecutionLib.validateCallGas(request.txnData.callGas, _EXTRA_GAS);
        is_valid[6] = ExecutionLib.validateToAddress(request.txnData.toAddress);

        return is_valid;
    }

    /*
     *  Initialize a new Request.
     */
    function initialize(Request storage self,
                        address[4] addressArgs,
                        uint[11] uintArgs,
                        bytes callData) returns (bool) {
        address[6] memory addressValues = [
            0x0,             // self.claimData.claimedBy
            addressArgs[0],  // self.meta.createdBy
            addressArgs[1],  // self.meta.owner
            addressArgs[2],  // self.paymentData.donationBenefactor
            0x0,             // self.paymentData.paymentBenefactor
            addressArgs[3]   // self.txnData.toAddress
        ];

        bool[3] memory boolValues = [false, false, false];

        uint[15] memory uintValues = [
            0,               // self.claimData.claimDeposit
            tx.gasprice,     // self.paymentData.anchorGasPrice
            uintArgs[0],     // self.paymentData.donation
            0,               // self.paymentData.donationOwed
            uintArgs[1],     // self.paymentData.payment
            0,               // self.paymentData.paymentOwed
            uintArgs[2],     // self.schedule.claimWindowSize
            uintArgs[3],     // self.schedule.freezePeriod
            uintArgs[4],     // self.schedule.reservedWindowSize
            uintArgs[5],     // self.schedule.temporalUnit
            uintArgs[6],     // self.schedule.windowStart
            uintArgs[7],     // self.schedule.windowSize
            uintArgs[8],     // self.txnData.callGas
            uintArgs[9],     // self.txnData.callValue
            uintArgs[10]     // self.txnData.requiredStackDepth
        ];

        uint8[1] memory uint8Values = [
            0
        ];

        deserialize(self, addressValues, boolValues, uintValues, uint8Values, callData);

        return true;
    }

    /*
     *  Returns the entire data structure of the Request in a *serialized*
     *  format.  This will be missing the `callData` which must be requested
     *  separately
     *
     *  Parameter order is alphabetical by type, then namespace, then name
     *
     *  TODO: figure out why this fails.
     */
    function serialize(Request storage self) returns (bool) {
        // Address values
        self.serializedValues.addressValues[0] = self.claimData.claimedBy;
        self.serializedValues.addressValues[1] = self.meta.createdBy;
        self.serializedValues.addressValues[2] = self.meta.owner;
        self.serializedValues.addressValues[3] = self.paymentData.donationBenefactor;
        self.serializedValues.addressValues[4] = self.paymentData.paymentBenefactor;
        self.serializedValues.addressValues[5] = self.txnData.toAddress;

        // Boolean values
        self.serializedValues.boolValues[0] = self.meta.isCancelled;
        self.serializedValues.boolValues[1] = self.meta.wasCalled;
        self.serializedValues.boolValues[2] = self.meta.wasSuccessful;

        // UInt256 values
        self.serializedValues.uintValues[0] = self.claimData.claimDeposit;
        self.serializedValues.uintValues[1] = self.paymentData.anchorGasPrice;
        self.serializedValues.uintValues[2] = self.paymentData.donation;
        self.serializedValues.uintValues[3] = self.paymentData.donationOwed;
        self.serializedValues.uintValues[4] = self.paymentData.payment;
        self.serializedValues.uintValues[5] = self.paymentData.paymentOwed;
        self.serializedValues.uintValues[6] = self.schedule.claimWindowSize;
        self.serializedValues.uintValues[7] = self.schedule.freezePeriod;
        self.serializedValues.uintValues[8] = self.schedule.reservedWindowSize;
        self.serializedValues.uintValues[9] = uint(self.schedule.temporalUnit);
        self.serializedValues.uintValues[10] = self.schedule.windowStart;
        self.serializedValues.uintValues[11] = self.schedule.windowSize;
        self.serializedValues.uintValues[12] = self.txnData.callGas;
        self.serializedValues.uintValues[13] = self.txnData.callValue;
        self.serializedValues.uintValues[14] = self.txnData.requiredStackDepth;

        // Uint8 values
        self.serializedValues.uint8Values[0] = self.claimData.paymentModifier;

        return true;
    }

    /*
     *  Populates a Request object from the full output of `serialize`.
     *
     *  Parameter order is alphabetical by type, then namespace, then name.
     */
    function deserialize(Request storage self,
                         address[6] addressValues,
                         bool[3] boolValues,
                         uint[15] uintValues,
                         uint8[1] uint8Values,
                         bytes callData) returns (bool) {
        // callData is special.
        self.txnData.callData = callData;

        // Address values
        self.claimData.claimedBy = addressValues[0];
        self.meta.createdBy = addressValues[1];
        self.meta.owner = addressValues[2];
        self.paymentData.donationBenefactor = addressValues[3];
        self.paymentData.paymentBenefactor = addressValues[4];
        self.txnData.toAddress = addressValues[5];

        // Boolean values
        self.meta.isCancelled = boolValues[0];
        self.meta.wasCalled = boolValues[1];
        self.meta.wasSuccessful = boolValues[2];

        // UInt values
        self.claimData.claimDeposit = uintValues[0];
        self.paymentData.anchorGasPrice = uintValues[1];
        self.paymentData.donation = uintValues[2];
        self.paymentData.donationOwed = uintValues[3];
        self.paymentData.payment = uintValues[4];
        self.paymentData.paymentOwed = uintValues[5];
        self.schedule.claimWindowSize = uintValues[6];
        self.schedule.freezePeriod = uintValues[7];
        self.schedule.reservedWindowSize = uintValues[8];
        self.schedule.temporalUnit = RequestScheduleLib.TemporalUnit(uintValues[9]);
        self.schedule.windowStart = uintValues[10];
        self.schedule.windowSize = uintValues[11];
        self.txnData.callGas = uintValues[12];
        self.txnData.callValue = uintValues[13];
        self.txnData.requiredStackDepth = uintValues[14];

        // Uint8 values
        self.claimData.paymentModifier = uint8Values[0];
    }

    enum Reason {
        WasCancelled,
        AlreadyCalled,
        BeforeCallWindow,
        AfterCallWindow,
        ReservedForClaimer,
        StackTooDeep,
        InsufficientGas
    }

    event Aborted(Reason reason);
    event Executed(uint payment, uint donation, uint measuredGasConsumption);

    function execute(Request storage self) returns (bool) {
        /*
         *  Send the requested transaction.
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
         *  6. if (msg.sender != tx.origin):
         *         - Verify stack can be increased by requiredStackDepth
         *  7. msg.gas >= callGas
         */
        var startGas = msg.gas;

        if (msg.gas < requiredExecutionGas(self)) {
            Aborted(Reason.InsufficientGas);
            return false;
        } else if (self.meta.wasCalled) {
            Aborted(Reason.AlreadyCalled);
            return false;
        } else if (self.meta.isCancelled) {
            Aborted(Reason.WasCancelled);
            return false;
        } else if (self.schedule.isBeforeWindow()) {
            Aborted(Reason.BeforeCallWindow);
            return false;
        } else if (self.schedule.isAfterWindow()) {
            Aborted(Reason.AfterCallWindow);
            return false;
        } else if (self.claimData.isClaimed() &&
                   msg.sender != self.claimData.claimedBy &&
                   self.schedule.inReservedWindow()) {
            Aborted(Reason.ReservedForClaimer);
            return false;
        } else if (msg.sender != tx.origin && !self.txnData.stackCanBeExtended()) {
            Aborted(Reason.StackTooDeep);
            return false;
        }

        // Ensure the request is marked as having been called before sending
        // the transaction to prevent re-entrance.
        self.meta.wasCalled = true;

        // Send the transaction
        self.meta.wasSuccessful = self.txnData.sendTransaction();

        if (self.paymentData.getDonation() == 0) throw;

        // Compute the donation amount
        if (self.paymentData.hasBenefactor()) {
            self.paymentData.donationOwed = self.paymentData.getDonation()
                                                            .safeAdd(self.paymentData.donationOwed);
        }

        // Compute the payment amount and who it should be sent do.
        self.paymentData.paymentBenefactor = msg.sender;
        if (self.claimData.isClaimed()) {
            self.paymentData.paymentOwed = self.claimData.claimDeposit.safeAdd(self.paymentData.paymentOwed);
            // need to zero out the claim deposit since it is now accounted for
            // in the paymentOwed value.
            self.claimData.claimDeposit = 0;
            self.paymentData.paymentOwed = self.paymentData.getPaymentWithModifier(self.claimData.paymentModifier)
                                                           .safeAdd(self.paymentData.paymentOwed);
        } else {
            self.paymentData.paymentOwed = self.paymentData.getPayment()
                                                           .safeAdd(self.paymentData.paymentOwed);
        }

        // Record the amount of gas used by execution.
        uint measuredGasConsumption = startGas.flooredSub(msg.gas).safeAdd(_EXTRA_GAS);

        // +--------------------------------------------------------------+
        // | NOTE: All code after this must be accounted for by EXTRA_GAS |
        // +--------------------------------------------------------------+

        // Add the gas reimbursment amount to the payment.
        self.paymentData.paymentOwed = measuredGasConsumption.safeMultiply(tx.gasprice)
                                                             .safeAdd(self.paymentData.paymentOwed);

        // Log the two payment amounts.  Otherwise it is non-trivial to figure
        // out how much was payed.
        Executed(self.paymentData.paymentOwed,
                 self.paymentData.donationOwed,
                 measuredGasConsumption);

        // Send the donation.
        self.paymentData.sendDonation();

        // Send the payment.
        self.paymentData.sendPayment();

        // Send all extra ether back to the owner.
        sendOwnerEther(self);

        return true;
    }

    function requiredExecutionGas(Request storage self) returns (uint) {
        return self.txnData.callGas.safeAdd(_GAS_TO_AUTHORIZE_EXECUTION)
                                   .safeAdd(_GAS_TO_COMPLETE_EXECUTION);
    }

    // TODO: compute this
    uint constant _GAS_TO_AUTHORIZE_EXECUTION = 0;

    /*
     * The amount of gas needed to do all of the pre execution checks.
     */
    function GAS_TO_AUTHORIZE_EXECUTION() returns (uint) {
        return _GAS_TO_AUTHORIZE_EXECUTION;
    }

    // TODO: compute this
    uint constant _GAS_TO_COMPLETE_EXECUTION = 190000;

    /*
     * The amount of gas needed to complete the execute method after
     * the transaction has been sent.
     */
    function GAS_TO_COMPLETE_EXECUTION() returns (uint) {
        return _GAS_TO_COMPLETE_EXECUTION;
    }

    // TODO: compute this
    uint constant _EXTRA_GAS = 185000;

    /*
     *  The amount of gas used by the portion of the `execute` function
     *  that cannot be accounted for via gas tracking.
     */
    function EXTRA_GAS() returns (uint) {
        return _EXTRA_GAS;
    }

    /*
     *  Return boolean whether the call can be cancelled.  Must satisfy the
     *  following conditions.
     *
     *  1. Not Cancelled
     *  2. either:
     *    * not wasCalled && afterExecutionWindow
     *    * not claimed && beforeFreezeWindow && msg.sender == owner
     */
    function isCancellable(Request storage self) returns (bool) {
        if (self.meta.isCancelled) {
            return false;
        } else if (!self.meta.wasCalled && self.schedule.isAfterWindow()) {
            return true;
        } else if (!self.claimData.isClaimed() && self.schedule.isBeforeFreeze() && msg.sender == self.meta.owner) {
            return true;
        } else {
            return false;
        }
    }

    /*
     *  Cancel the transaction request, attempting to send all appropriate
     *  refunds.
     */
    function cancel(Request storage self) returns (bool) {
        if (!isCancellable(self)) {
            return false;
        }

        // set this here to prevent re-entrance attacks.
        self.meta.isCancelled = true;

        // refund any claim deposit.
        self.claimData.refundDeposit();

        // send the remaining ether to the owner.
        sendOwnerEther(self);

        return true;
    }

    /*
     * Return boolean as to whether the request may be claimed.
     */
    function isClaimable(Request storage self) returns (bool) {
        if (self.claimData.isClaimed()) {
            return false;
        } else if (self.meta.isCancelled) {
            return false;
        } else if (!self.schedule.inClaimWindow()) {
            return false;
        } else if (msg.value < ClaimLib.minimumDeposit(self.paymentData.payment)) {
            return false;
        } else {
            return true;
        }
    }

    /*
     * Claim the request
     */
    function claim(Request storage self) returns (bool) {
        if (!isClaimable(self)) {
            if (msg.sender.sendOrThrow(msg.value)) {
                return false;
            }
            throw;
        }
        self.claimData.claim(self.schedule.computePaymentModifier());
    }

    /*
     * Refund claimer deposit.
     */
    function refundClaimDeposit(Request storage self) returns (bool) {
        if (self.meta.isCancelled || self.meta.wasCalled) {
            return self.claimData.refundDeposit(msg.gas);
        }
        return false;
    }

    /*
     * Send donation
     */
    function sendDonation(Request storage self) returns (bool) {
        if (self.meta.wasCalled) {
            return self.paymentData.sendDonation(msg.gas);
        }
        return false;
    }

    /*
     * Send payment
     */
    function sendPayment(Request storage self) returns (bool) {
        if (self.meta.wasCalled) {
            return self.paymentData.sendPayment(msg.gas);
        }
        return false;
    }

    /*
     * Send all extra ether in the request contract back to the owner.
     */
    function sendOwnerEther(Request storage self) returns (bool) {
        return sendOwnerEther(self, SafeSendLib.DEFAULT_SEND_GAS());
    }

    function sendOwnerEther(Request storage self, uint sendGas) returns (bool) {
        if (self.meta.isCancelled || self.meta.wasCalled) {
            self.meta.owner.safeSend(this.balance.flooredSub(self.claimData.claimDeposit)
                                                 .flooredSub(self.paymentData.paymentOwed)
                                                 .flooredSub(self.paymentData.donationOwed),
                                     sendGas);
            return true;
        }
        return false;
    }
}
