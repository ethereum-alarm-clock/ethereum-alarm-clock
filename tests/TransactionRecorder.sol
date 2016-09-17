contract TransactionRecorder {
    uint public lastCallValue;
    address public lastCaller;
    bytes public lastCallData;
    uint public lastCallGas;

    function () {
        lastCallGas = msg.gas;
        lastCallData = msg.data;
        lastCaller = msg.sender;
        lastCallValue = msg.value;
    }
}
