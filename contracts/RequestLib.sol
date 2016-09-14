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
        uintValues[3] = self.paymentData.anchorGasPrice;
        uintValues[4] = self.paymentData.donation;
        uintValues[5] = self.paymentData.payment;
        uintValues[6] = self.result.donationOwed;
        uintValues[7] = self.result.gasConsumption;
        uintValues[8] = self.result.paymentOwed;
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
        self.paymentData.anchorGasPrice = uintValues[3];
        self.paymentData.donation = uintValues[4];
        self.paymentData.payment = uintValues[5];
        self.result.donationOwed = uintValues[6];
        self.result.gasConsumption = uintValues[7];
        self.result.paymentOwed = uintValues[8];
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
                        address[5] addressValues,
                        uint[16] uintValues,
                        uint8[1] uint8Values,
                        bytes callData) returns (bool) {
        // TODO:
        throw;
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
        var nowValue = self.schedule.getNow();

        if (self.meta.isCancelled) {
            Aborted(Reason.WasCancelled);
            return false;
        } else if (self.result.wasCalled) {
            Aborted(Reason.AlreadyCalled);
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
        } else if (msg.gas < self.txnData.callGas) {
            Aborted(Reason.InsufficientGas);
            return false;
        }

        // Ensure the request is marked as having been called before sending
        // the transaction to prevent re-entrance.
        self.result.wasCalled = true;

        // Send the transaction
        self.result.wasSuccessful = self.txnData.sendTransaction();

        // Report execution back to the origin address.
        self.meta.reportExecution();

        // Compute the donation amount
        if (self.paymentData.hasBenefactor()) {
            self.result.donationOwed += self.paymentData.getDonation();
        }

        // Compute the payment amount
        if (self.claimData.isClaimed()) {
            self.result.paymentOwed += self.claimData.claimDeposit;
            self.result.paymentOwed += self.paymentData.getPaymentWithModifier(self.claimData.paymentModifier);
        } else {
            self.result.paymentOwed += self.paymentData.getPayment();
        }

        // Record the amount of gas used by execution.
        self.result.gasConsumption = startGas - msg.gas + EXTRA_GAS();

        // NOTE: All code after this must be accounted for by EXTRA_GAS

        // Add the gas reimbursment amount to the payment.
        self.result.paymentOwed += self.result.gasConsumption * tx.gasprice;

        // Log the two payment amounts.  Otherwise it is non-trivial to figure
        // out how much was payed.
        Executed(self.result.paymentOwed, self.result.donationOwed);

        // Send the donation.  This will be a noop if there is no benefactor or
        // if the donation amount is 0.
        self.result.donationOwed -= PaymentLib.safeSend(self.paymentData.donationBenefactor, self.result.donationOwed);

        // Send the payment.
        self.result.paymentOwed -= PaymentLib.safeSend(msg.sender, self.result.paymentOwed);

        return true;
    }

    // TODO: compute this
    uint constant _EXTRA_GAS = 0;

    /*
     *  Returns the amount of gas used by the portion of the `execute` function
     *  that cannot be accounted for via gas tracking.
     */
    function EXTRA_GAS() returns (uint) {
        return _EXTRA_GAS;
    }
}
