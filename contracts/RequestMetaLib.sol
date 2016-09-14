//pragma solidity 0.4.1;

import {RequestFactoryInterface} from "contracts/RequestFactoryInterface.sol";



library RequestMetaLib {
    struct RequestMeta {
        // The address that created this request
        address owner;

        // The address of the request factory that created this request.
        address factoryAddress;

        // Was the request cancelled.
        bool isCancelled;
    }

    function reportExecution(RequestMeta storage self) returns (bool) {
        var factory = RequestFactoryInterface(self.factoryAddress);
        return factory.receiveExecutionNotification();
    }
}
