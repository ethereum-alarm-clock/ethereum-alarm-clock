pragma solidity 0.4.24;

import "contracts/zeppelin/SafeMath.sol";

/**
 * @title RequestScheduleLib
 * @dev Library containing the logic for request scheduling.
 */
library RequestScheduleLib {
    using SafeMath for uint;

    /**
     * The manner in which this schedule specifies time.
     *
     * Null: present to require this value be explicitely specified
     * Blocks: execution schedule determined by block.number
     * Timestamp: execution schedule determined by block.timestamp
     */
    enum TemporalUnit {
        Null,           // 0
        Blocks,         // 1
        Timestamp       // 2
    }

    struct ExecutionWindow {

        TemporalUnit temporalUnit;      /// The type of unit used to measure time.

        uint windowStart;               /// The starting point in temporal units from which the transaction can be executed.

        uint windowSize;                /// The length in temporal units of the execution time period.

        uint freezePeriod;              /// The length in temporal units before the windowStart where no activity is allowed.

        uint reservedWindowSize;        /// The length in temporal units at the beginning of the executionWindow in which only the claim address can execute.

        uint claimWindowSize;           /// The length in temporal units before the freezeperiod in which an address can claim the execution.
    }

    /**
     * @dev Get the `now` represented in the temporal units assigned to this request.
     * @param self The ExecutionWindow object.
     * @return The unsigned integer representation of `now` in appropiate temporal units.
     */
    function getNow(ExecutionWindow storage self) 
        public view returns (uint)
    {
        return _getNow(self.temporalUnit);
    }

    /**
     * @dev Internal function to return the `now` based on the appropiate temporal units.
     * @param _temporalUnit The assigned TemporalUnit to this transaction.
     */
    function _getNow(TemporalUnit _temporalUnit) 
        internal view returns (uint)
    {
        if (_temporalUnit == TemporalUnit.Timestamp) {
            return block.timestamp;
        } 
        if (_temporalUnit == TemporalUnit.Blocks) {
            return block.number;
        }
        /// Only reaches here if the unit is unset, unspecified or unsupported.
        revert();
    }

    /**
     * @dev The modifier that will be applied to the bounty value depending
     * on when a call was claimed.
     */
    function computePaymentModifier(ExecutionWindow storage self) 
        internal view returns (uint8)
    {        
        uint paymentModifier = (getNow(self).sub(firstClaimBlock(self)))
            .mul(100)
            .div(self.claimWindowSize); 
        assert(paymentModifier <= 100); 

        return uint8(paymentModifier);
    }

    /*
     *  Helper: computes the end of the execution window.
     */
    function windowEnd(ExecutionWindow storage self)
        internal view returns (uint)
    {
        return self.windowStart.add(self.windowSize);
    }

    /*
     *  Helper: computes the end of the reserved portion of the execution
     *  window.
     */
    function reservedWindowEnd(ExecutionWindow storage self)
        internal view returns (uint)
    {
        return self.windowStart.add(self.reservedWindowSize);
    }

    /*
     *  Helper: computes the time when the request will be frozen until execution.
     */
    function freezeStart(ExecutionWindow storage self) 
        internal view returns (uint)
    {
        return self.windowStart.sub(self.freezePeriod);
    }

    /*
     *  Helper: computes the time when the request will be frozen until execution.
     */
    function firstClaimBlock(ExecutionWindow storage self) 
        internal view returns (uint)
    {
        return freezeStart(self).sub(self.claimWindowSize);
    }

    /*
     *  Helper: Returns boolean if we are before the execution window.
     */
    function isBeforeWindow(ExecutionWindow storage self)
        internal view returns (bool)
    {
        return getNow(self) < self.windowStart;
    }

    /*
     *  Helper: Returns boolean if we are after the execution window.
     */
    function isAfterWindow(ExecutionWindow storage self) 
        internal view returns (bool)
    {
        return getNow(self) > windowEnd(self);
    }

    /*
     *  Helper: Returns boolean if we are inside the execution window.
     */
    function inWindow(ExecutionWindow storage self)
        internal view returns (bool)
    {
        return self.windowStart <= getNow(self) && getNow(self) < windowEnd(self);
    }

    /*
     *  Helper: Returns boolean if we are inside the reserved portion of the
     *  execution window.
     */
    function inReservedWindow(ExecutionWindow storage self)
        internal view returns (bool)
    {
        return self.windowStart <= getNow(self) && getNow(self) < reservedWindowEnd(self);
    }

    /*
     * @dev Helper: Returns boolean if we are inside the claim window.
     */
    function inClaimWindow(ExecutionWindow storage self) 
        internal view returns (bool)
    {
        /// Checks that the firstClaimBlock is in the past or now.
        /// Checks that now is before the start of the freezePeriod.
        return firstClaimBlock(self) <= getNow(self) && getNow(self) < freezeStart(self);
    }

    /*
     *  Helper: Returns boolean if we are before the freeze period.
     */
    function isBeforeFreeze(ExecutionWindow storage self) 
        internal view returns (bool)
    {
        return getNow(self) < freezeStart(self);
    }

    /*
     *  Helper: Returns boolean if we are before the claim window.
     */
    function isBeforeClaimWindow(ExecutionWindow storage self)
        internal view returns (bool)
    {
        return getNow(self) < firstClaimBlock(self);
    }

    ///---------------
    /// VALIDATION
    ///---------------

    /**
     * @dev Validation: Ensure that the reservedWindowSize is less than or equal to the windowSize.
     * @param _reservedWindowSize The size of the reserved window.
     * @param _windowSize The size of the execution window.
     * @return True if the reservedWindowSize is within the windowSize.
     */
    function validateReservedWindowSize(uint _reservedWindowSize, uint _windowSize)
        public pure returns (bool)
    {
        return _reservedWindowSize <= _windowSize;
    }

    /**
     * @dev Validation: Ensure that the startWindow is at least freezePeriod amount of time in the future.
     * @param _temporalUnit The temporalUnit of this request.
     * @param _freezePeriod The freezePeriod in temporal units.
     * @param _windowStart The time in the future which represents the start of the execution window.
     * @return True if the windowStart is at least freezePeriod amount of time in the future.
     */
    function validateWindowStart(TemporalUnit _temporalUnit, uint _freezePeriod, uint _windowStart) 
        public view returns (bool)
    {
        return _getNow(_temporalUnit).add(_freezePeriod) <= _windowStart;
    }

    /*
     *  Validation: ensure that the temporal unit passed in is constrained to 0 or 1
     */
    function validateTemporalUnit(uint _temporalUnitAsUInt) 
        public pure returns (bool)
    {
        return (_temporalUnitAsUInt != uint(TemporalUnit.Null) &&
            (_temporalUnitAsUInt == uint(TemporalUnit.Blocks) ||
            _temporalUnitAsUInt == uint(TemporalUnit.Timestamp))
        );
    }
}
