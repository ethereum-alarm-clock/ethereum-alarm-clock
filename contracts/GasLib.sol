//pragma solidity 0.4.1;

import {MathLib} from "contracts/MathLib.sol";


library GasLib {
    using MathLib for uint;

    /*
     *  Returns a gas value that leaves at least reserveAmount leftover.  This
     *  may return 0 if msg.gas < reserveAmount.  The BUFFER value is present
     *  to prevent underflow in cases where msg.gas >= reserveAmount but the
     *  act of comparison drops msg.gas < reserveAmount.
     */
    uint constant _BUFFER = 10000;

    function BUFFER() returns (uint) {
        return _BUFFER;
    }

    function getGas(uint reserveAmount) returns (uint) {
        if (msg.gas < reserveAmount.safeAdd(_BUFFER)) {
            return 0;
        }
        return msg.gas.flooredSub(reserveAmount);
    }
}
