pragma solidity 0.4.19;

import "contracts/Interface/RequestFactoryInterface.sol";
import "contracts/Interface/RequestTrackerInterface.sol";
import "contracts/TransactionRequest.sol";
import "contracts/Library/RequestLib.sol";
import "contracts/IterTools.sol";

/**
 * @title RequestFactory
 * @dev Contract which will produce new TransactionRequests.
 */
contract RequestFactory is RequestFactoryInterface {
    using IterTools for bool[6];

    // RequestTracker of this contract.
    RequestTrackerInterface public requestTracker;

    function RequestFactory(address _trackerAddress) public {
        require( _trackerAddress != 0x0 );

        requestTracker = RequestTrackerInterface(_trackerAddress);
    }

    /**
     * @dev The lowest level interface for creating a transaction request.
     * 
     * @param _addressArgs [0] -  meta.owner
     * @param _addressArgs [1] -  paymentData.feeRecipient
     * @param _addressArgs [2] -  txnData.toAddress
     * @param _uintArgs [0]    -  paymentData.fee
     * @param _uintArgs [1]    -  paymentData.payment
     * @param _uintArgs [2]    -  schedule.claimWindowSize
     * @param _uintArgs [3]    -  schedule.freezePeriod
     * @param _uintArgs [4]    -  schedule.reservedWindowSize
     * @param _uintArgs [5]    -  schedule.temporalUnit
     * @param _uintArgs [6]    -  schedule.windowSize
     * @param _uintArgs [7]    -  schedule.windowStart
     * @param _uintArgs [8]    -  txnData.callGas
     * @param _uintArgs [9]    -  txnData.callValue
     * @param _uintArgs [10]   -  txnData.gasPrice
     * @param _uintArgs [11]   -  claimData.requiredDeposit
     * @param _callData        -  The call data
     */
    function createRequest(
        address[3]  _addressArgs,
        uint[12]    _uintArgs,
        bytes       _callData
    )
        public payable returns (address)
    {
        TransactionRequest request = (new TransactionRequest).value(msg.value)(
            [
                msg.sender,       // Created by
                _addressArgs[0],  // meta.owner
                _addressArgs[1],  // paymentData.feeRecipient
                _addressArgs[2]   // txnData.toAddress
            ],
            _uintArgs,            //uint[12]
            _callData
        );

        // Track the address locally
        requests[address(request)] = true;

        // Log the creation.
        RequestCreated(address(request), _addressArgs[0]);

        // Add the request to the RequestTracker
        requestTracker.addRequest(address(request), _uintArgs[7]); // windowStart

        return address(request);
    }

    /**
     *  The same as createRequest except that it requires validation prior to
     *  creation.
     *
     *  Parameters are the same as `createRequest`
     */
    function createValidatedRequest(
        address[3]  _addressArgs,
        uint[12]    _uintArgs,
        bytes       _callData
    ) 
        public payable returns (address)
    {
        bool[6] memory isValid = validateRequestParams(
            _addressArgs,
            _uintArgs,
            _callData,
            msg.value
        );

        if (!isValid.all()) {
            if (!isValid[0]) {
                ValidationError(uint8(Errors.InsufficientEndowment));
            }
            if (!isValid[1]) {
                ValidationError(uint8(Errors.ReservedWindowBiggerThanExecutionWindow));
            }
            if (!isValid[2]) {
                ValidationError(uint8(Errors.InvalidTemporalUnit));
            }
            if (!isValid[3]) {
                ValidationError(uint8(Errors.ExecutionWindowTooSoon));
            }
            if (!isValid[4]) {
                ValidationError(uint8(Errors.CallGasTooHigh));
            }
            if (!isValid[5]) {
                ValidationError(uint8(Errors.EmptyToAddress));
            }

            // Try to return the ether sent with the message.  If this failed
            // then revert() to force it to be returned
            if (!msg.sender.send(msg.value)) {
                revert();
            }
            return 0x0;
        }

        return createRequest(_addressArgs, _uintArgs, _callData);
    }

    /// ----------------------------
    /// Internal
    /// ----------------------------

    /*
     *  @dev The enum for launching `ValidationError` events and mapping them to an error.
     */
    enum Errors {
        InsufficientEndowment,
        ReservedWindowBiggerThanExecutionWindow,
        InvalidTemporalUnit,
        ExecutionWindowTooSoon,
        CallGasTooHigh,
        EmptyToAddress
    }

    event ValidationError(uint8 error);

    /*
     * @dev Validate the constructor arguments for either `createRequest` or `createValidatedRequest`.
     */
    function validateRequestParams(
        address[3]  _addressArgs,
        uint[12]    _uintArgs,
        bytes       _callData,
        uint        _endowment
    )
        public view returns (bool[6])
    {
        return RequestLib.validate(
            [
                msg.sender,      // meta.createdBy
                _addressArgs[0],  // meta.owner
                _addressArgs[1],  // paymentData.feeRecipient
                _addressArgs[2]   // txnData.toAddress
            ],
            _uintArgs,
            _callData,
            _endowment
        );
    }

    /// Mapping to hold known requests.
    mapping (address => bool) requests;

    function isKnownRequest(address _address) 
        public view returns (bool isKnown)
    {
        return requests[_address];
    }
}