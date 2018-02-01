pragma solidity 0.4.19;

contract RequestTrackerInterface {

    function getWindowStart(address factory, address request) 
        public view returns (uint);

    function getPreviousRequest(address factory, address request) 
        public view returns (address);

    function getNextRequest(address factory, address request) 
        public view returns (address);

    function addRequest(address request, uint startWindow) 
        public returns (bool);

    function removeRequest(address request) 
        public returns (bool);

    function isKnownRequest(address factory, address request) 
        public view returns (bool);

    function query(address factory, bytes2 operator, uint value) 
        public view returns (address);
    
}
