import {Proxy} from "tests/Proxy.sol";


contract DiggerProxy is Proxy {
    address public to;
    bytes public callData;

    function __dig_then_proxy(uint n, address _to, bytes _callData) public {
        to = _to;
        callData = _callData;
        __dig_then_proxy(n);
    }

    bool public result;

    function __dig_then_proxy(uint n) public {
        if (n == 0) {
            result = __proxy(to, callData);
        } else {
            if (!address(this).callcode(bytes4(sha3("__dig_then_proxy(uint256)")), n - 1)) throw;
        }
    }
}
