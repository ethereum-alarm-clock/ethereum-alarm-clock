//pragma solidity 0.4.1;


import {RequestScheduleLib} from "contracts/RequestScheduleLib.sol";
import {BaseScheduler} from "contracts/Scheduler.sol";


contract TimestampScheduler is BaseScheduler {
    function TimestampScheduler(address _factoryAddress) {
        // Set the type of time scheduling to timestamps
        temporalUnit = RequestScheduleLib.TemporalUnit(2);

        // Set the factory address.
        factoryAddress = _factoryAddress;
    }
}
