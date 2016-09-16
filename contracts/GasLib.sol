library GasLib {
    /*
     *  Returns a gas value that leaves at least reserveAmount leftover.  This
     *  may return 0 if msg.gas < reserveAmount.  The BUFFER value is present
     *  to prevent underflow in cases where msg.gas >= reserveAmount but the
     *  act of comparison drops msg.gas < reserveAmount.
     */
    uint constant BUFFER = 10000;

    function getGas(uint reserveAmount) returns (uint) {
        if (msg.gas < reserveAmount + BUFFER) {
            return 0;
        }
        return msg.gas - reserveAmount;
    }
}
