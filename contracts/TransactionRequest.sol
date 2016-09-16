//pragma solidity 0.4.1;

import {RequestLib} from "contracts/RequestLib.sol";
import {Digger} from "contracts/Digger.sol";


contract TransactionRequest is Digger {
    using RequestLib for RequestLib.Request;

    function TransactionRequest(address[3] addressArgs,
                                uint[11] uintArgs,
                                bytes callData) {
        address[4] memory addressValues = [
            msg.sender,      // meta.createdBy
            addressArgs[0],  // meta.owner
            addressArgs[1],  // paymentData.donationBenefactor
            addressArgs[2]   // txnData.toAddress
        ];
        txnRequest.initialize(addressValues, uintArgs, callData);
    }

    RequestLib.Request txnRequest;

    function execute() public returns (bool) {
        return txnRequest.execute();
    }

    function requestData() constant returns (address[5],
                                             bool[3],
                                             uint[16],
                                             uint8[1]) {
        return txnRequest.serialize();
    }

    function callData() constant returns (bytes) {
        return txnRequest.txnData.callData;
    }
}
