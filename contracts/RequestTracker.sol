//pragma solidity 0.4.1;

import {GroveLib} from "contracts/GroveLib.sol";
import {MathLib} from "contracts/MathLib.sol";


contract RequestTracker {
    /*
     * testnet: 0x8e67d439713b2022cac2ff4ebca21e173ccba4a0
     * mainnet: n/a
     */
    using GroveLib for GroveLib.Index;
    using MathLib for uint;

    mapping (address => GroveLib.Index) requestsByAddress;

    /*
     * Returns the windowStart value for the given request.
     */
    function getWindowStart(address factory, address request) constant returns (uint) {
        return uint(requestsByAddress[factory].getNodeValue(bytes32(request)));
    }

    /*
     * Returns the request which comes directly before the given request.
     */
    function getPreviousRequest(address factory, address request) constant returns (address) {
        return address(requestsByAddress[factory].getPreviousNode(bytes32(request)));
    }

    /*
     * Returns the request which comes directly after the given request.
     */
    function getNextRequest(address factory, address request) constant returns (address) {
        return address(requestsByAddress[factory].getNextNode(bytes32(request)));
    }

    /*
     * Add the given request.
     */
    function addRequest(address request, uint startWindow) returns (bool) {
        requestsByAddress[msg.sender].insert(bytes32(request), startWindow.safeCastSigned());
        return true;
    }

    /*
     * Remove the given address from the index.
     */
    function removeRequest(address request) constant returns (bool) {
        requestsByAddress[msg.sender].remove(bytes32(request));
        return true;
    }

    /*
     * Return boolean as to whether the given address is present for the given
     * factory.
     */
    function isKnownRequest(address factory, address request) constant returns (bool) {
        return requestsByAddress[factory].exists(bytes32(request));
    }

    /*
     * Query the index for the given factory.
     */
    function query(address factory, bytes2 operator, uint value) constant returns (address) {
        return address(requestsByAddress[factory].query(operator, value.safeCastSigned()));
    }
}
