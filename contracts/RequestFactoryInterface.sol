//pragma solidity 0.4.1;


contract RequestFactoryInterface {
    function createRequest(address[4] addressArgs,
                           uint[11] uintArgs,
                           bytes callData) returns (address);
    function receiveExecutionNotification() returns (bool);
    function isKnownRequest(address _address) returns (bool);
}
