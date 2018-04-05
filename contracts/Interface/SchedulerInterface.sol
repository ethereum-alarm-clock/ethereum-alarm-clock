pragma solidity ^0.4.21;

import "contracts/Library/RequestScheduleLib.sol";
import "contracts/Library/SchedulerLib.sol";

/**
 * @title SchedulerInterface
 * @dev The base contract that the higher contracts: BaseScheduler, BlockScheduler and TimestampScheduler all inherit from.
 */
contract SchedulerInterface {
    using SchedulerLib for SchedulerLib.FutureTransaction;

    // The RequestFactory address which produces requests for this scheduler.
    address public factoryAddress;
    
    // The TemporalUnit of this scheduler.
    RequestScheduleLib.TemporalUnit public temporalUnit;

    /*
     * Local storage variable used to house the data for transaction
     * scheduling.
     */
    SchedulerLib.FutureTransaction public futureTransaction;

    /*
     * When applied to a function, causes the local futureTransaction to
     * get reset to it's defaults on each function call.
     */
    modifier doReset {
        if (temporalUnit == RequestScheduleLib.TemporalUnit.Blocks) {
            futureTransaction.resetAsBlock();
        } else if (temporalUnit == RequestScheduleLib.TemporalUnit.Timestamp) {
            futureTransaction.resetAsTimestamp();
        } else {
            revert();
        }
        _;
    }
        
    function schedule(address   _toAddress, bytes _callData, uint[8] _uintArgs)
        doReset
        public payable returns (address);
}
