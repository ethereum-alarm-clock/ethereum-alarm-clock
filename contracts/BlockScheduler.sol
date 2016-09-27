//pragma solidity 0.4.1;


import {RequestScheduleLib} from "contracts/RequestScheduleLib.sol";
import {BaseScheduler} from "contracts/Scheduler.sol";


contract BlockScheduler is BaseScheduler {
    function BlockScheduler(address _trackerAddress,
                            address _factoryAddress) {
        // Set the type of time scheduling to blocks
        temporalUnit = RequestScheduleLib.TemporalUnit(1);

        // Set the tracker and factory addresses.
        trackerAddress = _trackerAddress;
        factoryAddress = _factoryAddress;
    }
}
