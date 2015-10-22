// String Utils v0.1

/// @title String Utils - String utility functions
/// @author Piper Merriam - <pipermerriam@gmail.com>
library StringLib {
    /*
     *  Address: 0x4f830b115c86d93a1a4e324548ef80b0f2dd4c76
     */

    /// @dev Converts an unsigned integert to its string representation.
    /// @param v The number to be converted.
    function uintToBytes(uint v) constant returns (bytes32 ret) {
        if (v == 0) {
            ret = '0';
        }
        else {
            while (v > 0) {
                ret = bytes32(uint(ret) / (2 ** 8));
                ret |= bytes32(((v % 10) + 48) * 2 ** (8 * 31));
                v /= 10;
            }
        }
        return ret;
    }

    /// @dev Converts a numeric string to it's unsigned integer representation.
    /// @param v The string to be converted.
    function bytesToUInt(bytes32 v) constant returns (uint ret) {
        if (v == 0x0) {
            throw;
        }

        uint digit;

        for (uint i = 0; i < 32; i++) {
            digit = uint((uint(v) / (2 ** (8 * (31 - i)))) & 0xff);
            if (digit == 0) {
                break;
            }
            else if (digit < 48 || digit > 57) {
                throw;
            }
            ret *= 10;
            ret += (digit - 48);
        }
        return ret;
    }
}
