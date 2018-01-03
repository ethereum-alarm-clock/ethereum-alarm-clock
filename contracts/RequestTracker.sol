pragma solidity ^0.4.18;

import "contracts/Interface/RequestTrackerInterface.sol";
import "contracts/Library/GroveLib.sol";
import "contracts/Library/MathLib.sol";

/**
 * @title RequestTracker
 * @dev The API for the GroveLib backend that keeps track of transaction requests.
 */
contract RequestTracker is RequestTrackerInterface {
    using GroveLib for GroveLib.Index;

    mapping (address => GroveLib.Index) requestsByAddress;

    /*
     * @dev Returns the windowStart value for the given request.
     */
    function getWindowStart(address factory, address request)
        public view returns (uint)
    {
        return uint(requestsByAddress[factory].getNodeValue(bytes32(request)));
    }

    /*
     * @dev Returns the request which comes directly before the given request.
     */
    function getPreviousRequest(address factory, address request)
        public view returns (address)
    {
        return address(requestsByAddress[factory].getPreviousNode(bytes32(request)));
    }

    /*
     * @dev Returns the request which comes directly after the given request.
     */
    function getNextRequest(address factory, address request)
        public view returns (address)
    {
        return address(requestsByAddress[factory].getNextNode(bytes32(request)));
    }

    /*
     * Add the given request.
     */
    function addRequest(address request, uint startWindow) 
        public returns (bool)
    {
        requestsByAddress[msg.sender].insert(bytes32(request), MathLib.safeCastSigned(startWindow));
        return true;
    }

    /*
     * Remove the given address from the index.
     */
    function removeRequest(address request)
        public returns (bool)
    {
        requestsByAddress[msg.sender].remove(bytes32(request));
        return true;
    }

    /*
     * Return boolean as to whether the given address is present for the given
     * factory.
     */
    function isKnownRequest(address factory, address request)
        public view returns (bool)
    {
        return requestsByAddress[factory].exists(bytes32(request));
    }

    /*
     * Query the index for the given factory.
     */
    function query(address factory, bytes2 operator, uint value)
        public view returns (address)
    {
        return address(requestsByAddress[factory].query(operator, MathLib.safeCastSigned(value)));
    }
}