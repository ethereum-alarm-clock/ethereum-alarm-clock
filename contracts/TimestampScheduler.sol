//pragma solidity 0.4.1;


import {RequestScheduleLib} from "contracts/RequestScheduleLib.sol";
import {BaseScheduler} from "contracts/Scheduler.sol";


contract TimestampScheduler is BaseScheduler {
    function TimestampScheduler(address _trackerAddress,
                                address _factoryAddress)
             BaseScheduler(_trackerAddress,
                           _factoryAddress,
                           uint(RequestScheduleLib.TemporalUnit.Timestamp)) {
    }
}
