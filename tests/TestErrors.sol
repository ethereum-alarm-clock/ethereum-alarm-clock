import {Proxy} from "tests/Proxy.sol";


contract ErrorGenerator is Proxy {
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
}
