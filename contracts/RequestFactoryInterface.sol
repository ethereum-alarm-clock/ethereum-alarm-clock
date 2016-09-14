//pragma solidity 0.4.1;


contract RequestFactoryInterface {
    function receiveExecutionNotification() returns (bool);
    function isKnownRequest(address _address) returns (bool);
}
