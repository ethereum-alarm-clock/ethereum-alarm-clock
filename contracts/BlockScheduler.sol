//pragma solidity 0.4.1;


import {RequestScheduleLib} from "contracts/RequestScheduleLib.sol";
import {BaseScheduler} from "contracts/Scheduler.sol";


contract BlockScheduler is BaseScheduler {
    function BlockScheduler(address _trackerAddress,
                            address _factoryAddress)
             BaseScheduler(_trackerAddress,
                           _factoryAddress,
                           1) {
                           //uint(RequestScheduleLib.TemporalUnit.Blocks)) {
    }
}
