pragma solidity 0.4.24;

library MathLib {
    uint constant INT_MAX = 57896044618658097711785492504343953926634992332820282019728792003956564819967;  // 2**255 - 1
    /*
     * Subtracts b from a in a manner such that zero is returned when an
     * underflow condition is met.
     */
    // function flooredSub(uint a, uint b) returns (uint) {
    //     if (b >= a) {
    //         return 0;
    //     } else {
    //         return a - b;
    //     }
    // }

    // /*
    //  * Adds b to a in a manner that throws an exception when overflow
    //  * conditions are met.
    //  */
    // function safeAdd(uint a, uint b) returns (uint) {
    //     if (a + b >= a) {
    //         return a + b;
    //     } else {
    //         throw;
    //     }
    // }

    // /*
    //  * Multiplies a by b in a manner that throws an exception when overflow
    //  * conditions are met.
    //  */
    // function safeMultiply(uint a, uint b) returns (uint) {
    //     var result = a * b;
    //     if (b == 0 || result / b == a) {
    //         return a * b;
    //     } else {
    //         throw;
    //     }
    // }

    /*
     * Return the larger of a or b.  Returns a if a == b.
     */
    function max(uint a, uint b) 
        public pure returns (uint)
    {
        if (a >= b) {
            return a;
        } else {
            return b;
        }
    }

    /*
     * Return the larger of a or b.  Returns a if a == b.
     */
    function min(uint a, uint b) 
        public pure returns (uint)
    {
        if (a <= b) {
            return a;
        } else {
            return b;
        }
    }

    /*
     * Returns a represented as a signed integer in a manner that throw an
     * exception if casting to signed integer would result in a negative
     * number.
     */
    function safeCastSigned(uint a) 
        public pure returns (int)
    {
        assert(a <= INT_MAX);
        return int(a);
    }
    
}
