library IterTools {
    /*
     *  Return true if any of the values in the boolean array are true
     */
    function all(bool[7] values) returns (bool) {
        for (uint i = 0; i < values.length; i++) {
            if (!values[i]) {
                return false;
            }
        }
        return true;
    }
}
