//pragma solidity 0.4.1;


import {RequestScheduleLib} from "contracts/RequestScheduleLib.sol";
import {BaseScheduler} from "contracts/Scheduler.sol";


contract TimestampScheduler is BaseScheduler {
    function TimestampScheduler(address _trackerAddress,
                                address _factoryAddress) {
        // Set the type of time scheduling to timestamps
        temporalUnit = RequestScheduleLib.TemporalUnit(2);

        // Set the tracker and factory addresses.
        trackerAddress = _trackerAddress;
        factoryAddress = _factoryAddress;
    }
}
