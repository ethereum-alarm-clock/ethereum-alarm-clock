pragma solidity 0.4.24;

import "contracts/Interface/RequestFactoryInterface.sol";
import "contracts/TransactionRequestCore.sol";
import "contracts/Library/RequestLib.sol";
import "contracts/IterTools.sol";
import "contracts/CloneFactory.sol";
import "contracts/Library/RequestScheduleLib.sol";

import "openzeppelin-solidity/contracts/lifecycle/Pausable.sol";

/**
 * @title RequestFactory
 * @dev Contract which will produce new TransactionRequests.
 */
contract RequestFactory is RequestFactoryInterface, CloneFactory, Pausable {
    using IterTools for bool[6];

    TransactionRequestCore public transactionRequestCore;

    uint constant public BLOCKS_BUCKET_SIZE = 240; //~1h
    uint constant public TIMESTAMP_BUCKET_SIZE = 3600; //1h

    constructor(
        address _transactionRequestCore
    ) 
        public 
    {
        require(_transactionRequestCore != 0x0);

        transactionRequestCore = TransactionRequestCore(_transactionRequestCore);
    }

    /**
     * @dev The lowest level interface for creating a transaction request.
     *
     * @param _addressArgs [0] -  meta.owner
     * @param _addressArgs [1] -  paymentData.feeRecipient
     * @param _addressArgs [2] -  txnData.toAddress
     * @param _uintArgs [0]    -  paymentData.fee
     * @param _uintArgs [1]    -  paymentData.bounty
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
        whenNotPaused
        public payable returns (address)
    {
        // Create a new transaction request clone from transactionRequestCore.
        address transactionRequest = createClone(transactionRequestCore);

        // Call initialize on the transaction request clone.
        TransactionRequestCore(transactionRequest).initialize.value(msg.value)(
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
        requests[transactionRequest] = true;

        // Log the creation.
        emit RequestCreated(
            transactionRequest,
            _addressArgs[0],
            getBucket(_uintArgs[7], RequestScheduleLib.TemporalUnit(_uintArgs[5])),
            _uintArgs
        );

        return transactionRequest;
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
            msg.value
        );

        if (!isValid.all()) {
            if (!isValid[0]) {
                emit ValidationError(uint8(Errors.InsufficientEndowment));
            }
            if (!isValid[1]) {
                emit ValidationError(uint8(Errors.ReservedWindowBiggerThanExecutionWindow));
            }
            if (!isValid[2]) {
                emit ValidationError(uint8(Errors.InvalidTemporalUnit));
            }
            if (!isValid[3]) {
                emit ValidationError(uint8(Errors.ExecutionWindowTooSoon));
            }
            if (!isValid[4]) {
                emit ValidationError(uint8(Errors.CallGasTooHigh));
            }
            if (!isValid[5]) {
                emit ValidationError(uint8(Errors.EmptyToAddress));
            }

            // Try to return the ether sent with the message
            msg.sender.transfer(msg.value);
            
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

    function getBucket(uint windowStart, RequestScheduleLib.TemporalUnit unit)
        public pure returns(int)
    {
        uint bucketSize;
        /* since we want to handle both blocks and timestamps
            and do not want to get into case where buckets overlaps
            block buckets are going to be negative ints
            timestamp buckets are going to be positive ints
            we'll overflow after 2**255-1 blocks instead of 2**256-1 since we encoding this on int256
        */
        int sign;

        if (unit == RequestScheduleLib.TemporalUnit.Blocks) {
            bucketSize = BLOCKS_BUCKET_SIZE;
            sign = -1;
        } else if (unit == RequestScheduleLib.TemporalUnit.Timestamp) {
            bucketSize = TIMESTAMP_BUCKET_SIZE;
            sign = 1;
        } else {
            revert();
        }
        return sign * int(windowStart - (windowStart % bucketSize));
    }
}
