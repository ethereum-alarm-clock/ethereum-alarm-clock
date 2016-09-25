//pragma solidity 0.4.1;

import {MathLib} from "contracts/MathLib.sol";


library RequestScheduleLib {
    using MathLib for uint;

    /*
     *  The manner in which this schedule specifies time.
     *
     *  Null: present to require this value be explicitely specified
     *  Blocks: execution schedule determined by block.number
     *  Timestamp: execution schedule determined by block.timestamp
     */
    enum TemporalUnit {
        Null,
        Blocks,
        Timestamp
    }

    struct ExecutionWindow {
        // The type of unit used to measure time.
        TemporalUnit temporalUnit;

        // The temporal starting point when the request may be executed
        uint windowStart;

        // The number of temporal units past the windowStart that the request
        // may still be executed.
        uint windowSize;

        // The number of temporal units before the window start during which no
        // activity may occur.
        uint freezePeriod;

        // The number of temporal units after the windowStart during which only
        // the address that claimed the request may execute the request.
        uint reservedWindowSize;

        // The number of temporal units that prior to the call freeze window
        // during which the request will be claimable.
        uint claimWindowSize;
    }

    /*
     *  Return what `now` is in the temporal units being used by this request.
     *  Currently supports block based times, and timestamp (seconds) based
     *  times.
     */
    function getNow(ExecutionWindow storage self) returns (uint) {
        return getNow(self.temporalUnit);
    }

    function getNow(TemporalUnit temporalUnit) internal returns (uint) {
        if (temporalUnit == TemporalUnit.Timestamp) {
            return now;
        } else if (temporalUnit == TemporalUnit.Blocks) {
            return block.number;
        } else {
            // Unsupported unit.
            throw;
        }
    }

    /*
     * The modifier that will be applied to the payment value for a claimed call.
     */
    function computePaymentModifier(ExecutionWindow storage self) returns (uint8) {
        if (!inClaimWindow(self)) {
            throw;
        }
        uint paymentModifier = getNow(self).flooredSub(firstClaimBlock(self))
                                           .safeMultiply(100) / self.claimWindowSize;
        if (paymentModifier > 100) {
            throw;
        }
        return uint8(paymentModifier);
    }

    /*
     *  Helper: computes the end of the execution window.
     */
    function windowEnd(ExecutionWindow storage self) returns (uint) {
        return self.windowStart.safeAdd(self.windowSize);
    }

    /*
     *  Helper: computes the end of the reserved portion of the execution
     *  window.
     */
    function reservedWindowEnd(ExecutionWindow storage self) returns (uint) {
        return self.windowStart.safeAdd(self.reservedWindowSize);
    }

    /*
     *  Helper: computes the time when the request will be frozen until execution.
     */
    function freezeStart(ExecutionWindow storage self) returns (uint) {
        return self.windowStart.flooredSub(self.freezePeriod);
    }

    /*
     *  Helper: computes the time when the request will be frozen until execution.
     */
    function firstClaimBlock(ExecutionWindow storage self) returns (uint) {
        return freezeStart(self).flooredSub(self.claimWindowSize);
    }

    /*
     *  Helper: Returns boolean if we are before the execution window.
     */
    function isBeforeWindow(ExecutionWindow storage self) returns (bool) {
        return getNow(self) < self.windowStart;
    }

    /*
     *  Helper: Returns boolean if we are after the execution window.
     */
    function isAfterWindow(ExecutionWindow storage self) returns (bool) {
        return getNow(self) > windowEnd(self);
    }

    /*
     *  Helper: Returns boolean if we are inside the execution window.
     */
    function inWindow(ExecutionWindow storage self) returns (bool) {
        return self.windowStart <= getNow(self) && getNow(self) < windowEnd(self);
    }

    /*
     *  Helper: Returns boolean if we are inside the reserved portion of the
     *  execution window.
     */
    function inReservedWindow(ExecutionWindow storage self) returns (bool) {
        return self.windowStart <= getNow(self) && getNow(self) < reservedWindowEnd(self);
    }

    /*
     *  Helper: Returns boolean if we are inside the claim window.
     */
    function inClaimWindow(ExecutionWindow storage self) returns (bool) {
        return firstClaimBlock(self) <= getNow(self) && getNow(self) < freezeStart(self);
    }

    /*
     *  Helper: Returns boolean if we are before the freeze period.
     */
    function isBeforeFreeze(ExecutionWindow storage self) returns (bool) {
        return getNow(self) < freezeStart(self);
    }

    /*
     *  Helper: Returns boolean if we are before the freeze period.
     */
    function isBeforeClaimWindow(ExecutionWindow storage self) returns (bool) {
        return getNow(self) < firstClaimBlock(self);
    }

    /*
     *  Validation: ensure that the reservedWindowSize <= windowSize
     */
    function validateReservedWindowSize(uint reservedWindowSize,
                                        uint windowSize) returns (bool) {
        return reservedWindowSize < windowSize;
    }

    /*
     *  Validation: ensure that the startWindow is at least freezePeriod in the future
     */
    function validateWindowStart(TemporalUnit temporalUnit,
                                 uint freezePeriod,
                                 uint windowStart) returns (bool) {
        return getNow(temporalUnit).safeAdd(freezePeriod) <= windowStart;
    }

    /*
     *  Validation: ensure that the temporal unit passed in is constrained to 0 or 1
     */
    function validateTemporalUnit(uint temporalUnitAsUInt) returns (bool) {
        return (temporalUnitAsUInt != uint(TemporalUnit.Null) && (
            temporalUnitAsUInt == uint(TemporalUnit.Blocks) || 
            temporalUnitAsUInt == uint(TemporalUnit.Timestamp)
        ));
    }
}
