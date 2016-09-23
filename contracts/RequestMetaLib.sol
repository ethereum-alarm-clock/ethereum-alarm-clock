//pragma solidity 0.4.1;


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
}
