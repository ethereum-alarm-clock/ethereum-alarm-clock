import {Proxy} from "tests/Proxy.sol";


contract TransactionRecorder is Proxy {
    bool public wasCalled;

    uint public lastCallValue;
    address public lastCaller;
    bytes public lastCallData;
    uint public lastCallGas;

    function () {
        lastCallGas = msg.gas;
        lastCallData = msg.data;
        lastCaller = msg.sender;
        lastCallValue = msg.value;
        wasCalled = true;
    }

    function __reset__() public {
        lastCallGas = 0;
        lastCallData = '';
        lastCaller = 0x0;
        lastCallValue = 0;
        wasCalled = false;
    }
}
