//pragma solidity 0.4.1;


import {RequestScheduleLib} from "contracts/RequestScheduleLib.sol";
import {SchedulerInterface} from "contracts/SchedulerInterface.sol";
import {SchedulerLib} from "contracts/SchedulerLib.sol";


contract BaseScheduler is SchedulerInterface {
    using SchedulerLib for SchedulerLib.FutureTransaction;

    /*
     * Fallback function to be able to receive ether.  This can occur
     * legidimately when scheduling fails due to a validation error.
     */
    function() {
    }

    /*
     *  Full scheduling API exposing all fields.
     * 
     *  uintArgs[0] callGas
     *  uintArgs[1] callValue
     *  uintArgs[2] windowSize
     *  uintArgs[3] windowStart
     *  bytes callData;
     *  address toAddress;
     */
    function scheduleTransaction(address toAddress,
                                 bytes callData,
                                 uint[4] uintArgs) doReset public returns (address) {
        futureTransaction.toAddress = toAddress;
        futureTransaction.callData = callData;
        futureTransaction.callGas = uintArgs[0];
        futureTransaction.callValue = uintArgs[1];
        futureTransaction.windowSize = uintArgs[2];
        futureTransaction.windowStart = uintArgs[3];

        // This is here to make this explicit.  While it should remain the same
        // across multiple calls, this ensures that it is clear what this value
        // is set to as well as keeping the setting close to where the other
        // transaction details are set.
        futureTransaction.temporalUnit = temporalUnit;

        return futureTransaction.schedule(factoryAddress, trackerAddress);
    }

    /*
     *  Full scheduling API exposing all fields.
     * 
     *  uintArgs[0] callGas
     *  uintArgs[1] callValue
     *  uintArgs[2] donation
     *  uintArgs[3] payment
     *  uintArgs[4] requiredStackDepth
     *  uintArgs[5] windowSize
     *  uintArgs[6] windowStart
     *  bytes callData;
     *  address toAddress;
     */
    function scheduleTransaction(address toAddress,
                                 bytes callData,
                                 uint[7] uintArgs) doReset public returns (address) {
        futureTransaction.toAddress = toAddress;
        futureTransaction.callData = callData;
        futureTransaction.callGas = uintArgs[0];
        futureTransaction.callValue = uintArgs[1];
        futureTransaction.donation = uintArgs[2];
        futureTransaction.payment = uintArgs[3];
        futureTransaction.requiredStackDepth = uintArgs[4];
        futureTransaction.windowSize = uintArgs[5];
        futureTransaction.windowStart = uintArgs[6];

        // This is here to make this explicit.  While it should remain the same
        // across multiple calls, this ensures that it is clear what this value
        // is set to as well as keeping the setting close to where the other
        // transaction details are set.
        futureTransaction.temporalUnit = temporalUnit;

        return futureTransaction.schedule(factoryAddress, trackerAddress);
    }
}
