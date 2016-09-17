contract ErrorGenerator {
    function doThrow() {
        doThrow(true);
    }

    function doThrow(bool shouldThrow) {
        if (shouldThrow) {
            throw;
        }
    }

    function() {
        throw;
    }

    function __proxy(address to, bytes callData) returns (bool) {
        return to.call(callData);
    }
}
