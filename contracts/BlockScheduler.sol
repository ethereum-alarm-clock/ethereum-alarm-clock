//pragma solidity 0.4.1;


import {RequestScheduleLib} from "contracts/RequestScheduleLib.sol";
import {BaseScheduler} from "contracts/Scheduler.sol";


contract BlockScheduler is BaseScheduler {
    function BlockScheduler(address _factoryAddress) {
        // Set the type of time scheduling to blocks
        temporalUnit = RequestScheduleLib.TemporalUnit(1);

        // Set the factory address.
        factoryAddress = _factoryAddress;
    }
}
