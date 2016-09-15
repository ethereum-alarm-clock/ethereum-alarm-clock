//pragma solidity 0.4.1;

import {RequestFactoryInterface} from "contracts/RequestFactoryInterface.sol";
import {TransactionRequest} from "contracts/TransactionRequest.sol";
import {RequestLib} from "contracts/RequestLib.sol";
import {IterTools} from "contracts/IterTools.sol";


contract RequestFactory is RequestFactoryInterface {
    using IterTools for bool[7];

    /*
     *  Error Codes
     */
    event InsufficientEndowment();
    event ReservedWindowBiggerThanExecutionWindow();
    event InvalidTemporalUnit();
    event ExecutionWindowTooSoon();
    event InvalidRequiredStackDepth();
    event CallGasTooHigh();
    event EmptyToAddress();

    /*
     *  The full interface for
     */
    function createRequest(address[2] addressArgs,
                           uint[11] uintArgs,
                           bytes callData) returns (address) {
        var errors = RequestLib.validate(
            [address(this), msg.sender, addressArgs[0], addressArgs[1]],
            uintArgs,
            callData,
            msg.value
        );

        if (errors.any()) {
            if (errors[0]) InsufficientEndowment();
            if (errors[1]) ReservedWindowBiggerThanExecutionWindow();
            if (errors[2]) InvalidTemporalUnit();
            if (errors[3]) ExecutionWindowTooSoon();
            if (errors[4]) InvalidRequiredStackDepth();
            if (errors[5]) CallGasTooHigh();
            if (errors[6]) EmptyToAddress();
        }

        var request = (new TransactionRequest).value(msg.value)(
            [msg.sender, addressArgs[0], addressArgs[1]],
            uintArgs,
            callData
        );

        // TODO: register with tracker

        return request;
    }

    function receiveExecutionNotification() returns (bool) {
        // TODO;
        throw;
    }

    mapping (address => bool) requests;

    function isKnownRequest(address _address) returns (bool) {
        // TODO: decide whether this should be a local mapping or from tracker.
        return requests[_address];
    }
}

