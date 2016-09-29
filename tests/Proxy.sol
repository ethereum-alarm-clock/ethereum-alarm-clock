contract Proxy {
    function __proxy(address to) returns (bool) {
        return to.call.value(msg.value)();
    }

    function __proxy(address to, bytes callData) returns (bool) {
        return to.call.value(msg.value)(callData);
    }

    function __proxy(address to, bytes callData, uint callGas) returns (bool) {
        return to.call.value(msg.value).gas(callGas)(callData);
    }

    function() {
    }
}
