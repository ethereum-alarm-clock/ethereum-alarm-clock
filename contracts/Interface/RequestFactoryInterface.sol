pragma solidity ^0.4.18;

contract RequestFactoryInterface {

    event RequestCreated(address request);

    function createRequest(address[3] addressArgs,
                           uint[11] uintArgs,
                           bytes callData)
        public payable returns (address);

    function createValidatedRequest(address[3] addressArgs,
                                    uint[11] uintArgs,
                                    bytes callData) 
        public payable returns (address);

    function validateRequestParams(address[3] addressArgs,
                                   uint[11] uintArgs,
                                   bytes callData,
                                   uint endowment) 
        public returns (bool[6]);

    function isKnownRequest(address _address)
        public view returns (bool);
}
