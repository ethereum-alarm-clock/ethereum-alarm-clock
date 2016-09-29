//pragma solidity 0.4.1;


contract TransactionRequestInterface {
    /*
     *  Primary actions
     */
    function execute() public returns (bool);
    function cancel() public returns (bool);
    function claim() public returns (bool);

    /*
     *  Data accessors
     */
    function requestData() constant returns (address[6],
                                             bool[3],
                                             uint[15],
                                             uint8[1]);
    function callData() constant returns (bytes);

    /*
     *  Pull mechanisms for payments.
     */
    function refundClaimDeposit() public returns (bool);
    function sendDonation() public returns (bool);
    function sendPayment() public returns (bool);
    function sendOwnerEther() public returns (bool);
}
