//pragma solidity 0.4.1;

import {RequestLib} from "contracts/RequestLib.sol";
import {Digger} from "contracts/Digger.sol";


contract TransactionRequest is Digger {
    using RequestLib for RequestLib.Request;

    RequestLib.Request txnRequest;

    function execute() public returns (bool) {
        return txnRequest.execute();
    }
}
