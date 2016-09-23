import {Proxy} from "tests/Proxy.sol";


contract ErrorGenerator is Proxy {
    bool public shouldThrow;

    function ErrorGenerator() {
        shouldThrow = true;
    }

    function toggle() {
        shouldThrow = !shouldThrow;
    }

    function doThrow() {
        doThrow(shouldThrow);
    }

    function doThrow(bool _shouldThrow) {
        if (_shouldThrow) {
            throw;
        }
    }

    function() {
        if (shouldThrow) {
            throw;
        }
    }
}
