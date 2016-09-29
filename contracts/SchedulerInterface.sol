//pragma solidity 0.4.1;


import {RequestScheduleLib} from "contracts/RequestScheduleLib.sol";
import {SchedulerLib} from "contracts/SchedulerLib.sol";


contract SchedulerInterface {
    using SchedulerLib for SchedulerLib.FutureTransaction;

    address public factoryAddress;

    RequestScheduleLib.TemporalUnit public temporalUnit;

    /*
     * Local storage variable used to house the data for transaction
     * scheduling.
     */
    SchedulerLib.FutureTransaction futureTransaction;

    /*
     * When applied to a function, causes the local futureTransaction to
     * get reset to it's defaults on each function call.
     *
     * TODO: Compare to actual enum values when solidity compiler error is fixed.
     * https://github.com/ethereum/solidity/issues/1116
     */
    modifier doReset {
        if (uint(temporalUnit) == 1) {
            futureTransaction.resetAsBlock();
        } else if (uint(temporalUnit) == 2) {
            futureTransaction.resetAsTimestamp();
        } else {
            throw;
        }
        _ 
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
                                 uint[4] uintArgs) doReset public returns (address);

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
                                 uint[7] uintArgs) doReset public returns (address);
}
