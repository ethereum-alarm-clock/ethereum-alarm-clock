pragma solidity 0.4.24;

import "contracts/Interface/RequestFactoryInterface.sol";
import "contracts/Interface/SchedulerInterface.sol";

import "contracts/Library/PaymentLib.sol";
import "contracts/Library/RequestLib.sol";
import "contracts/Library/RequestScheduleLib.sol";

/**
 * @title BaseScheduler
 * @dev The foundational contract which provides the API for scheduling future transactions on the Alarm Client.
 */
contract BaseScheduler is SchedulerInterface {
    // The RequestFactory which produces requests for this scheduler.
    address public factoryAddress;

    // The TemporalUnit (Block or Timestamp) for this scheduler.
    RequestScheduleLib.TemporalUnit public temporalUnit;

    // The address which will be sent the fee payments.
    address public feeRecipient;

    /*
     * @dev Fallback function to be able to receive ether. This can occur
     *  legitimately when scheduling fails due to a validation error.
     */
    function() public payable {}

    /// Event that bubbles up the address of new requests made with this scheduler.
    event NewRequest(address request);

    /**
     * @dev Schedules a new TransactionRequest using the 'full' parameters.
     * @param _toAddress The address destination of the transaction.
     * @param _callData The bytecode that will be included with the transaction.
     * @param _uintArgs [0] The callGas of the transaction.
     * @param _uintArgs [1] The value of ether to be sent with the transaction.
     * @param _uintArgs [2] The size of the execution window of the transaction.
     * @param _uintArgs [3] The (block or timestamp) of when the execution window starts.
     * @param _uintArgs [4] The gasPrice which will be used to execute this transaction.
     * @param _uintArgs [5] The fee attached to this transaction.
     * @param _uintArgs [6] The bounty attached to this transaction.
     * @param _uintArgs [7] The deposit required to claim this transaction.
     * @return The address of the new TransactionRequest.   
     */ 
    function schedule (
        address   _toAddress,
        bytes     _callData,
        uint[8]   _uintArgs
    )
        public payable returns (address newRequest)
    {
        RequestFactoryInterface factory = RequestFactoryInterface(factoryAddress);

        uint endowment = computeEndowment(
            _uintArgs[6], //bounty
            _uintArgs[5], //fee
            _uintArgs[0], //callGas
            _uintArgs[1], //callValue
            _uintArgs[4]  //gasPrice
        );

        require(msg.value >= endowment);

        if (temporalUnit == RequestScheduleLib.TemporalUnit.Blocks) {
            newRequest = factory.createValidatedRequest.value(msg.value)(
                [
                    msg.sender,                 // meta.owner
                    feeRecipient,               // paymentData.feeRecipient
                    _toAddress                  // txnData.toAddress
                ],
                [
                    _uintArgs[5],               // paymentData.fee
                    _uintArgs[6],               // paymentData.bounty
                    255,                        // scheduler.claimWindowSize
                    10,                         // scheduler.freezePeriod
                    16,                         // scheduler.reservedWindowSize
                    uint(temporalUnit),         // scheduler.temporalUnit (1: block, 2: timestamp)
                    _uintArgs[2],               // scheduler.windowSize
                    _uintArgs[3],               // scheduler.windowStart
                    _uintArgs[0],               // txnData.callGas
                    _uintArgs[1],               // txnData.callValue
                    _uintArgs[4],               // txnData.gasPrice
                    _uintArgs[7]                // claimData.requiredDeposit
                ],
                _callData
            );
        } else if (temporalUnit == RequestScheduleLib.TemporalUnit.Timestamp) {
            newRequest = factory.createValidatedRequest.value(msg.value)(
                [
                    msg.sender,                 // meta.owner
                    feeRecipient,               // paymentData.feeRecipient
                    _toAddress                  // txnData.toAddress
                ],
                [
                    _uintArgs[5],               // paymentData.fee
                    _uintArgs[6],               // paymentData.bounty
                    60 minutes,                 // scheduler.claimWindowSize
                    3 minutes,                  // scheduler.freezePeriod
                    5 minutes,                  // scheduler.reservedWindowSize
                    uint(temporalUnit),         // scheduler.temporalUnit (1: block, 2: timestamp)
                    _uintArgs[2],               // scheduler.windowSize
                    _uintArgs[3],               // scheduler.windowStart
                    _uintArgs[0],               // txnData.callGas
                    _uintArgs[1],               // txnData.callValue
                    _uintArgs[4],               // txnData.gasPrice
                    _uintArgs[7]                // claimData.requiredDeposit
                ],
                _callData
            );
        } else {
            // unsupported temporal unit
            revert();
        }

        require(newRequest != 0x0);
        emit NewRequest(newRequest);
        return newRequest;
    }

    function computeEndowment(
        uint _bounty,
        uint _fee,
        uint _callGas,
        uint _callValue,
        uint _gasPrice
    )
        public view returns (uint)
    {
        return PaymentLib.computeEndowment(
            _bounty,
            _fee,
            _callGas,
            _callValue,
            _gasPrice,
            RequestLib.getEXECUTION_GAS_OVERHEAD()
        );
    }
}
