pragma solidity 0.4.24;

/**
 * @title IterTools
 * @dev Utility library that iterates through a boolean array of length 6.
 */
library IterTools {
    /*
     * @dev Return true if all of the values in the boolean array are true.
     * @param _values A boolean array of length 6.
     * @return True if all values are true, False if _any_ are false.
     */
    function all(bool[6] _values) 
        public pure returns (bool)
    {
        for (uint i = 0; i < _values.length; i++) {
            if (!_values[i]) {
                return false;
            }
        }
        return true;
    }
}
