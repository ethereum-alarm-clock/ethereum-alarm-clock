//pragma solidity 0.4.1;

import {ExecutionLib} from "contracts/ExecutionLib.sol";
import {ScheduleLib} from "contracts/ScheduleLib.sol";
import {ClaimLib} from "contracts/ClaimLib.sol";
import {RequestMetaLib} from "contracts/RequestMetaLib.sol";
import {PaymentLib} from "contracts/PaymentLib.sol";


library RequestLib {
    using ExecutionLib for ExecutionLib.ExecutionData;
    using ScheduleLib for ScheduleLib.Schedule;
    using ClaimLib for ClaimLib.ClaimData;
    using RequestMetaLib for RequestMetaLib.RequestMeta;
    using PaymentLib for PaymentLib.PaymentData;

    struct Result {
        bool wasCalled;
        bool wasSuccessful;
        uint gasConsumption;
        uint paymentOwed;
        uint donationOwed;
    }

    struct Request {
        ExecutionLib.ExecutionData txnData;
        Result result;
        RequestMetaLib.RequestMeta meta;
        PaymentLib.PaymentData paymentData;
        ClaimLib.ClaimData claimData;
        ScheduleLib.Schedule schedule;
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
    event Executed(uint payment, uint donation);

    /*
     *  Returns the entire data structure of the Request in a *serialized*
     *  format.  This will be missing the `callData` which must be requested
     *  separately
     *
     *  Parameter order is alphabetical by type, then namespace, then name
     */
    function serialize(Request storage self) returns (address[5] addressValues,
                                                      bool[3] boolValues,
                                                      uint[16] uintValues,
                                                      uint8[1] uint8Values) {
        // Address values
        addressValues[0] = self.claimData.claimedBy;
        addressValues[1] = self.meta.createdBy;
        addressValues[2] = self.meta.owner;
        addressValues[3] = self.paymentData.donationBenefactor;
        addressValues[4] = self.txnData.toAddress;

        // Boolean values
        boolValues[0] = self.meta.isCancelled;
        boolValues[1] = self.result.wasCalled;
        boolValues[2] = self.result.wasSuccessful;

        // UInt256 values
        uintValues[0] = self.claimData.claimDeposit;
        uintValues[1] = self.claimData.claimWindowSize;
        uintValues[2] = self.paymentData.anchorGasPrice;
        uintValues[3] = self.paymentData.donation;
        uintValues[4] = self.paymentData.payment;
        uintValues[5] = self.result.donationOwed;
        uintValues[6] = self.result.gasConsumption;
        uintValues[7] = self.result.paymentOwed;
        uintValues[8] = self.schedule.freezePeriod;
        uintValues[9] = self.schedule.reservedWindowSize;
        uintValues[10] = uint(self.schedule.temporalUnit);
        uintValues[11] = self.schedule.windowStart;
        uintValues[12] = self.schedule.windowSize;
        uintValues[13] = self.txnData.callGas;
        uintValues[14] = self.txnData.callValue;
        uintValues[15] = self.txnData.requiredStackDepth;

        // Uint8 values
        uint8Values[0] = self.claimData.paymentModifier;

        return (
            addressValues,
            boolValues,
            uintValues,
            uint8Values
        );
    }

    /*
     *  Populates a Request object from the full output of `serialize`.
     *
     *  Parameter order is alphabetical by type, then namespace, then name.
     */
    function deserialize(Request storage self,
                         address[5] addressValues,
                         bool[3] boolValues,
                         uint[16] uintValues,
                         uint8[1] uint8Values,
                         bytes callData) returns (bool) {
        // callData is special.
        self.txnData.callData = callData;

        // Address values
        self.claimData.claimedBy = addressValues[0];
        self.meta.createdBy = addressValues[1];
        self.meta.owner = addressValues[2];
        self.paymentData.donationBenefactor = addressValues[3];
        self.txnData.toAddress = addressValues[4];

        // Boolean values
        self.meta.isCancelled = boolValues[0];
        self.result.wasCalled = boolValues[1];
        self.result.wasSuccessful = boolValues[2];

        // UInt values
        self.claimData.claimDeposit = uintValues[0];
        self.claimData.claimWindowSize = uintValues[1];
        self.paymentData.anchorGasPrice = uintValues[2];
        self.paymentData.donation = uintValues[3];
        self.paymentData.payment = uintValues[4];
        self.result.donationOwed = uintValues[5];
        self.result.gasConsumption = uintValues[6];
        self.result.paymentOwed = uintValues[7];
        self.schedule.freezePeriod = uintValues[8];
        self.schedule.reservedWindowSize = uintValues[9];
        self.schedule.temporalUnit = ScheduleLib.TemporalUnit(uintValues[10]);
        self.schedule.windowStart = uintValues[11];
        self.schedule.windowSize = uintValues[12];
        self.txnData.callGas = uintValues[13];
        self.txnData.callValue = uintValues[14];
        self.txnData.requiredStackDepth = uintValues[15];

        // Uint8 values
        self.claimData.paymentModifier = uint8Values[0];
    }

    function initialize(Request storage self,
                        address[4] addressArgs,
                        uint[11] uintArgs,
                        bytes callData) returns (bool) {
        address[5] memory addressValues = [
            0x0,             // self.claimData.claimedBy
            addressArgs[0],  // self.meta.createdBy
            addressArgs[1],  // self.meta.owner
            addressArgs[2],  // self.paymentData.donationBenefactor
            addressArgs[3]   // self.txnData.toAddress
        ];

        bool[3] memory boolValues = [false, false, false];

        uint[16] memory uintValues = [
            0,               // self.claimData.claimDeposit
            uintArgs[0],     // self.claimData.claimWindowSize
            tx.gasprice,     // self.paymentData.anchorGasPrice
            uintArgs[1],     // self.paymentData.donation
            uintArgs[2],     // self.paymentData.payment
            0,               // self.result.donationOwed
            0,               // self.result.gasConsumption
            0,               // self.result.paymentOwed
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

    function validate(address[4] addressValues,
                      uint[11] uintValues,
                      bytes callData,
                      uint endowment) returns (bool[7] errors) {
        Request memory request;

        // callData is special.
        request.txnData.callData = callData;

        // Address values
        request.claimData.claimedBy = 0x0;
        request.meta.createdBy = addressValues[0];
        request.meta.owner = addressValues[1];
        request.paymentData.donationBenefactor = addressValues[2];
        request.txnData.toAddress = addressValues[3];

        // Boolean values
        request.meta.isCancelled = false;
        request.result.wasCalled = false;
        request.result.wasSuccessful = false;

        // UInt values
        request.claimData.claimDeposit = 0;
        request.claimData.claimWindowSize = uintValues[0];
        request.paymentData.anchorGasPrice = tx.gasprice;
        request.paymentData.donation = uintValues[1];
        request.paymentData.payment = uintValues[2];
        request.result.donationOwed = 0;
        request.result.gasConsumption = 0;
        request.result.paymentOwed = 0;
        request.schedule.freezePeriod = uintValues[3];
        request.schedule.reservedWindowSize = uintValues[4];
        request.schedule.temporalUnit = ScheduleLib.TemporalUnit(uintValues[5]);
        request.schedule.windowStart = uintValues[6];
        request.schedule.windowSize = uintValues[7];
        request.txnData.callGas = uintValues[8];
        request.txnData.callValue = uintValues[9];
        request.txnData.requiredStackDepth = uintValues[10];

        // Uint8 values
        request.claimData.paymentModifier = 0;

        // These errors must be in the same order as the RequestFactory.Errors
        // enum.
        errors[0] = PaymentLib.validateEndowment(endowment,
                                                 request.paymentData.payment,
                                                 request.paymentData.donation,
                                                 request.txnData.callGas,
                                                 request.txnData.callValue);
        errors[1] = ScheduleLib.validateReservedWindowSize(request.schedule.reservedWindowSize,
                                                           request.schedule.windowSize);
        errors[2] = ScheduleLib.validateTemporalUnit(uintValues[5]);
        errors[3] = ScheduleLib.validateWindowStart(request.schedule.temporalUnit,
                                                    request.schedule.freezePeriod,
                                                    request.schedule.windowStart);
        errors[4] = ExecutionLib.validateRequiredStackDepth(request.txnData.requiredStackDepth);
        errors[5] = ExecutionLib.validateCallGas(request.txnData.callGas, _EXTRA_GAS);
        errors[6] = ExecutionLib.validateToAddress(request.txnData.toAddress);

        return errors;
    }

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
        } else if (self.result.wasCalled) {
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
        self.result.wasCalled = true;

        // Send the transaction
        self.result.wasSuccessful = self.txnData.sendTransaction();

        // Report execution back to the origin address.
        self.meta.reportExecution(_GAS_TO_COMPLETE_EXECUTION);

        uint paymentOwed;
        uint donationOwed;

        // Compute the donation amount
        if (self.paymentData.hasBenefactor()) {
            donationOwed += self.paymentData.getDonation();
        }

        // Compute the payment amount
        if (self.claimData.isClaimed()) {
            paymentOwed += self.claimData.claimDeposit;
            paymentOwed += self.paymentData.getPaymentWithModifier(self.claimData.paymentModifier);
        } else {
            paymentOwed += self.paymentData.getPayment();
        }

        // Record the amount of gas used by execution.
        self.result.gasConsumption = (startGas - msg.gas) + EXTRA_GAS();

        // NOTE: All code after this must be accounted for by EXTRA_GAS

        // Add the gas reimbursment amount to the payment.
        paymentOwed += self.result.gasConsumption * tx.gasprice;

        // Log the two payment amounts.  Otherwise it is non-trivial to figure
        // out how much was payed.
        Executed(paymentOwed, donationOwed);

        // Send the donation.  This will be a noop if there is no benefactor or
        // if the donation amount is 0.
        donationOwed -= PaymentLib.safeSend(self.paymentData.donationBenefactor, donationOwed);

        // Send the payment.
        paymentOwed -= PaymentLib.safeSend(msg.sender, paymentOwed);

        // These need to be set after the send so that there is not opportunity
        // for re-entrance.
        self.result.donationOwed = donationOwed;
        self.result.paymentOwed = paymentOwed;

        return true;
    }

    function requiredExecutionGas(Request storage self) returns (uint) {
        return self.txnData.callGas +
               _GAS_TO_COMPLETE_EXECUTION +
               _GAS_TO_AUTHORIZE_EXECUTION +
               2 * PaymentLib.DEFAULT_SEND_GAS();
    }

    // TODO: compute this
    uint constant _GAS_TO_AUTHORIZE_EXECUTION = 200000;

    /*
     * The amount of gas needed to do all of the pre execution checks.
     */
    function GAS_TO_AUTHORIZE_EXECUTION() returns (uint) {
        return _GAS_TO_AUTHORIZE_EXECUTION;
    }

    // TODO: compute this
    uint constant _GAS_TO_COMPLETE_EXECUTION = 200000;

    /*
     * The amount of gas needed to complete the execute method after
     * the transaction has been sent.
     */
    function GAS_TO_COMPLETE_EXECUTION() returns (uint) {
        return _GAS_TO_COMPLETE_EXECUTION;
    }

    // TODO: compute this
    uint constant _EXTRA_GAS = 0;

    /*
     *  The amount of gas used by the portion of the `execute` function
     *  that cannot be accounted for via gas tracking.
     */
    function EXTRA_GAS() returns (uint) {
        return _EXTRA_GAS;
    }
}
