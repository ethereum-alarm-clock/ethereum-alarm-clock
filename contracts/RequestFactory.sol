//pragma solidity 0.4.1;

import {RequestFactoryInterface} from "contracts/RequestFactoryInterface.sol";
import {TransactionRequest} from "contracts/TransactionRequest.sol";
import {RequestLib} from "contracts/RequestLib.sol";
import {IterTools} from "contracts/IterTools.sol";


contract RequestFactory is RequestFactoryInterface {
    using IterTools for bool[7];

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
     *  The lowest level interface for creating a transaction request.
     *
     *  addressArgs[0]: paymentData.donationBenefactor
     *  addressArgs[1]: txnData.toAddress
     *  uintArgs[0],    claimData.claimWindowSize
     *  uintArgs[1],    paymentData.donation
     *  uintArgs[2],    paymentData.payment
     *  uintArgs[3],    schedule.freezePeriod
     *  uintArgs[4],    schedule.reservedWindowSize
     *  uintArgs[5],    schedule.temporalUnit
     *  uintArgs[6],    schedule.windowStart
     *  uintArgs[7],    schedule.windowSize
     *  uintArgs[8],    txnData.callGas
     *  uintArgs[9],    txnData.callValue
     *  uintArgs[10]    txnData.requiredStackDepth
     */
    function createRequest(address[2] addressArgs,
                           uint[11] uintArgs,
                           bytes callData) returns (address) {
        var errors = RequestLib.validate(
            [
                address(this),   // meta.createdBy
                msg.sender,      // meta.owner
                addressArgs[0],  // paymentData.donationBenefactor
                addressArgs[1]   // txnData.toAddress
            ],
            uintArgs,
            callData,
            msg.value
        );

        if (errors.any()) {
            if (errors[0]) ValidationError(Errors.InsufficientEndowment);
            if (errors[1]) ValidationError(Errors.ReservedWindowBiggerThanExecutionWindow);
            if (errors[2]) ValidationError(Errors.InvalidTemporalUnit);
            if (errors[3]) ValidationError(Errors.ExecutionWindowTooSoon);
            if (errors[4]) ValidationError(Errors.InvalidRequiredStackDepth);
            if (errors[5]) ValidationError(Errors.CallGasTooHigh);
            if (errors[6]) ValidationError(Errors.EmptyToAddress);
        }

        var request = (new TransactionRequest).value(msg.value)(
            [
                msg.sender,      // meta.owner
                addressArgs[0],  // paymentData.donationBenefactor
                addressArgs[1]   // txnData.toAddress
            ],
            uintArgs,
            callData
        );

        RequestCreated(address(request));

        // TODO: register with tracker

        return request;
    }

    function receiveExecutionNotification() returns (bool) {
        // TODO handle this.
        throw;
    }

    mapping (address => bool) requests;

    function isKnownRequest(address _address) returns (bool) {
        // TODO: decide whether this should be a local mapping or from tracker.
        return requests[_address];
    }
}

