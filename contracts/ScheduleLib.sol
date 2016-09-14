//pragma solidity 0.4.1;


library ScheduleLib {
    enum TemporalUnit {
        Seconds,
        Blocks
    }

    struct Schedule {
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
    }

    /*
     *  Return what `now` is in the temporal units being used by this request.
     *  Currently supports block based times, and timestamp (seconds) based
     *  times.
     */
    function getNow(Schedule storage self) returns (uint) {
        if (self.temporalUnit == TemporalUnit.Seconds) {
            return now;
        } else if (self.temporalUnit == TemporalUnit.Blocks) {
            return block.number;
        } else {
            // Unsupported unit.
            throw;
        }
    }

    /*
     *  Helper: computes the end of the execution window.
     */
    function windowEnd(Schedule storage self) returns (uint) {
        return self.windowStart + self.windowSize;
    }

    /*
     *  Helper: computes the end of the reserved portion of the execution
     *  window.
     */
    function reservedWindowEnd(Schedule storage self) returns (uint) {
        return self.windowStart + self.reservedWindowSize;
    }

    /*
     *  Helper: Returns boolean if we are before the execution window.
     */
    function isBeforeWindow(Schedule storage self) returns (bool) {
        return getNow(self) < self.windowStart;
    }

    /*
     *  Helper: Returns boolean if we are after the execution window.
     */
    function isAfterWindow(Schedule storage self) returns (bool) {
        return getNow(self) > self.windowStart;
    }

    /*
     *  Helper: Returns boolean if we are inside the execution window.
     */
    function inWindow(Schedule storage self) returns (bool) {
        return self.windowStart <= getNow(self) && getNow(self) <= windowEnd(self);
    }

    /*
     *  Helper: Returns boolean if we are inside the reserved portion of the
     *  execution window.
     */
    function inReservedWindow(Schedule storage self) returns (bool) {
        return self.windowStart <= getNow(self) && getNow(self) <= reservedWindowEnd(self);
    }
}
