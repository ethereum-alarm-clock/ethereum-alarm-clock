//pragma solidity 0.4.1;


contract RequestTrackerInterface {
    function getWindowStart(address scheduler, address request) constant returns (uint);
    function getPreviousRequest(address scheduler, address request) constant returns (address);
    function getNextRequest(address scheduler, address request) constant returns (address);
    function addRequest(address request, uint startWindow) constant returns (bool);
    function removeRequest(address request) constant returns (bool);
    function isKnownRequest(address scheduler, address request) constant returns (bool);
    function query(address scheduler, bytes2 operator, uint value) constant returns (address);
}
