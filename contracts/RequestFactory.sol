//pragma solidity 0.4.1;

import {RequestFactoryInterface} from "contracts/RequestFactoryInterface.sol";
import {TransactionRequest} from "contracts/TransactionRequest.sol";
import {RequestLib} from "contracts/RequestLib.sol";
import {SafeSendLib} from "contracts/SafeSendLib.sol";
import {IterTools} from "contracts/IterTools.sol";


contract RequestFactory is RequestFactoryInterface {
    using IterTools for bool[7];
    using SafeSendLib for address;

    /*
     *  The lowest level interface for creating a transaction request.
     *
     *  addressArgs[1] -  meta.owner
     *  addressArgs[1] -  paymentData.donationBenefactor
     *  addressArgs[2] -  txnData.toAddress
     *  uintArgs[0]    -  paymentData.donation
     *  uintArgs[1]    -  paymentData.payment
     *  uintArgs[2]    -  schedule.claimWindowSize
     *  uintArgs[3]    -  schedule.freezePeriod
     *  uintArgs[4]    -  schedule.reservedWindowSize
     *  uintArgs[5]    -  schedule.temporalUnit
     *  uintArgs[6]    -  schedule.windowSize
     *  uintArgs[7]    -  schedule.windowStart
     *  uintArgs[8]    -  txnData.callGas
     *  uintArgs[9]    -  txnData.callValue
     *  uintArgs[10]   -  txnData.requiredStackDepth
     */
    function createRequest(address[3] addressArgs,
                           uint[11] uintArgs,
                           bytes callData) returns (address) {
        var request = (new TransactionRequest).value(msg.value)(
            [
                msg.sender,
                addressArgs[0],  // meta.owner
                addressArgs[1],  // paymentData.donationBenefactor
                addressArgs[2]   // txnData.toAddress
            ],
            uintArgs,
            callData
        );

        // Track the address locally
        requests[address(request)] = true;

        // Log the creation.
        RequestCreated(address(request));

        return request;
    }

    /*
     *  ValidationError
     */
    enum Errors {
        InsufficientEndowment,
        ReservedWindowBiggerThanExecutionWindow,
        InvalidTemporalUnit,
        ExecutionWindowTooSoon,
        InvalidRequiredStackDepth,
        CallGasTooHigh,
        EmptyToAddress
    }

    event ValidationError(Errors error);

    /*
     * Validate the constructor arguments for either `createRequest` or
     * `createValidatedRequest`
     */
    function validateRequestParams(address[3] addressArgs,
                                   uint[11] uintArgs,
                                   bytes callData,
                                   uint endowment) returns (bool[7]) {
        return RequestLib.validate(
            [
                msg.sender,      // meta.createdBy
                addressArgs[0],  // meta.owner
                addressArgs[1],  // paymentData.donationBenefactor
                addressArgs[2]   // txnData.toAddress
            ],
            uintArgs,
            callData,
            endowment
        );
    }

    /*
     *  The same as createRequest except that it requires validation prior to
     *  creation.
     *
     *  Parameters are the same as `createRequest`
     */
    function createValidatedRequest(address[3] addressArgs,
                                    uint[11] uintArgs,
                                    bytes callData) returns (address) {
        var is_valid = validateRequestParams(addressArgs,
                                             uintArgs,
                                             callData,
                                             msg.value);

        if (!is_valid.all()) {
            if (!is_valid[0]) ValidationError(Errors.InsufficientEndowment);
            if (!is_valid[1]) ValidationError(Errors.ReservedWindowBiggerThanExecutionWindow);
            if (!is_valid[2]) ValidationError(Errors.InvalidTemporalUnit);
            if (!is_valid[3]) ValidationError(Errors.ExecutionWindowTooSoon);
            if (!is_valid[4]) ValidationError(Errors.InvalidRequiredStackDepth);
            if (!is_valid[5]) ValidationError(Errors.CallGasTooHigh);
            if (!is_valid[6]) ValidationError(Errors.EmptyToAddress);

            // Try to return the ether sent with the message.  If this failed
            // then throw to force it to be returned.
            if (msg.sender.sendOrThrow(msg.value)) {
                return 0x0;
            }
            throw;
        }

        return createRequest(addressArgs, uintArgs, callData);
    }

    mapping (address => bool) requests;

    function isKnownRequest(address _address) returns (bool) {
        // TODO: decide whether this should be a local mapping or from tracker.
        return requests[_address];
    }
}

