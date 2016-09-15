//pragma solidity 0.4.1;

import {RequestLib} from "contracts/RequestLib.sol";
import {Digger} from "contracts/Digger.sol";


contract TransactionRequest is Digger {
    using RequestLib for RequestLib.Request;

    function TransactionRequest(address[3] addressArgs,
                                uint[11] uintArgs,
                                bytes callData) {
        address[4] memory addressValues = [
            msg.sender,
            addressArgs[0],
            addressArgs[1],
            addressArgs[2]
        ];
        txnRequest.initialize(addressValues, uintArgs, callData);
    }

    RequestLib.Request txnRequest;

    function execute() public returns (bool) {
        return txnRequest.execute();
    }
}
