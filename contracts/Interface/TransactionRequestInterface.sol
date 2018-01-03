pragma solidity ^0.4.18;

contract TransactionRequestInterface {
    
    // Primary actions
    function execute() public returns (bool);
    function cancel() public returns (bool);
    function claim() public payable returns (bool);

    // Proxy function
    function proxy(address recipient, bytes callData)
        public payable returns (bool);

    // Data accessors
    function requestData() public view returns (address[6],
                                                bool[3],
                                                uint[14],
                                                uint8[1]);

    function callData() public view returns (bytes);

    // Pull mechanisms for payments.
    function refundClaimDeposit() public;
    function sendDonation() public returns (bool);
    function sendPayment() public returns (bool);
    function sendOwnerEther() public returns (bool);
}
