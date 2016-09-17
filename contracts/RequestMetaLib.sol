//pragma solidity 0.4.1;

import {GasLib} from "contracts/GasLib.sol";



library RequestMetaLib {
    struct RequestMeta {
        // The address that created this request
        address owner;

        // The address of the request factory that created this request.
        address createdBy;

        // Was the request cancelled.
        bool isCancelled;
        
        // Was the request called.
        bool wasCalled;

        // Was the return value from the call successful.
        bool wasSuccessful;
    }

    function reportExecution(RequestMeta storage self, uint gasReserve) returns (bool) {
        return self.createdBy.call.
                              gas(GasLib.getGas(gasReserve))
                              (bytes4(sha3("receiveExecutionNotification()")));
    }
}
