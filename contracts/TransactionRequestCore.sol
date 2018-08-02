pragma solidity 0.4.24;

import "contracts/Library/RequestLib.sol";
import "contracts/Library/RequestScheduleLib.sol";
import "contracts/Interface/TransactionRequestInterface.sol";

contract TransactionRequestCore is TransactionRequestInterface {
    using RequestLib for RequestLib.Request;
    using RequestScheduleLib for RequestScheduleLib.ExecutionWindow;

    RequestLib.Request txnRequest;
    bool private initialized = false;

    /*
     *  addressArgs[0] - meta.createdBy
     *  addressArgs[1] - meta.owner
     *  addressArgs[2] - paymentData.feeRecipient
     *  addressArgs[3] - txnData.toAddress
     *
     *  uintArgs[0]  - paymentData.fee
     *  uintArgs[1]  - paymentData.bounty
     *  uintArgs[2]  - schedule.claimWindowSize
     *  uintArgs[3]  - schedule.freezePeriod
     *  uintArgs[4]  - schedule.reservedWindowSize
     *  uintArgs[5]  - schedule.temporalUnit
     *  uintArgs[6]  - schedule.windowSize
     *  uintArgs[7]  - schedule.windowStart
     *  uintArgs[8]  - txnData.callGas
     *  uintArgs[9]  - txnData.callValue
     *  uintArgs[10] - txnData.gasPrice
     *  uintArgs[11] - claimData.requiredDeposit
     */
    function initialize(
        address[4]  addressArgs,
        uint[12]    uintArgs,
        bytes       callData
    )
        public payable
    {
        require(!initialized);

        txnRequest.initialize(addressArgs, uintArgs, callData);
        initialized = true;
    }

    /*
     *  Allow receiving ether.  This is needed if there is a large increase in
     *  network gas prices.
     */
    function() public payable {}

    /*
     *  Actions
     */
    function execute() public returns (bool) {
        return txnRequest.execute();
    }

    function cancel() public returns (bool) {
        return txnRequest.cancel();
    }

    function claim() public payable returns (bool) {
        return txnRequest.claim();
    }

    /*
     *  Data accessor functions.
     */

    // Declaring this function `view`, although it creates a compiler warning, is
    // necessary to return values from it.
    function requestData()
        public view returns (address[6], bool[3], uint[15], uint8[1])
    {
        return txnRequest.serialize();
    }

    function callData()
        public view returns (bytes data)
    {
        data = txnRequest.txnData.callData;
    }

    /**
     * @dev Proxy a call from this contract to another contract.
     * This function is only callable by the scheduler and can only
     * be called after the execution window ends. One purpose is to
     * provide a way to transfer assets held by this contract somewhere else.
     * For example, if this request was used to buy tokens during an ICO,
     * it would become the owner of the tokens and this function would need
     * to be called with the encoded data to the token contract to transfer
     * the assets somewhere else. */
    function proxy(address _to, bytes _data)
        public payable returns (bool success)
    {
        require(txnRequest.meta.owner == msg.sender && txnRequest.schedule.isAfterWindow());
        
        /* solium-disable-next-line */
        return _to.call.value(msg.value)(_data);
    }

    /*
     *  Pull based payment functions.
     */
    function refundClaimDeposit() public returns (bool) {
        txnRequest.refundClaimDeposit();
    }

    function sendFee() public returns (bool) {
        return txnRequest.sendFee();
    }

    function sendBounty() public returns (bool) {
        return txnRequest.sendBounty();
    }

    function sendOwnerEther() public returns (bool) {
        return txnRequest.sendOwnerEther();
    }

    function sendOwnerEther(address recipient) public returns (bool) {
        return txnRequest.sendOwnerEther(recipient);
    }

    /** Event duplication from RequestLib.sol. This is so
     *  that these events are available on the contracts ABI.*/
    event Aborted(uint8 reason);
    event Cancelled(uint rewardPayment, uint measuredGasConsumption);
    event Claimed();
    event Executed(uint bounty, uint fee, uint measuredGasConsumption);
}
