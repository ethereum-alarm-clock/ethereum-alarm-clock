pragma solidity 0.4.24;

contract TransactionRequestInterface {
    
    // Primary actions
    function execute() public returns (bool);
    function cancel() public returns (bool);
    function claim() public payable returns (bool);

    // Proxy function
    function proxy(address recipient, bytes callData) public payable returns (bool);

    // Data accessors
    function requestData() public view returns (address[6], bool[3], uint[15], uint8[1]);
    function callData() public view returns (bytes);

    // Pull mechanisms for payments.
    function refundClaimDeposit() public returns (bool);
    function sendFee() public returns (bool);
    function sendBounty() public returns (bool);
    function sendOwnerEther() public returns (bool);
    function sendOwnerEther(address recipient) public returns (bool);
}
