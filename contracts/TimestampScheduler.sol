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


contract TestnetTimestampScheduler is TimestampScheduler(0x6005cb5aa9c4774c9f1f46ef3323c1337809cdb0) {
}
