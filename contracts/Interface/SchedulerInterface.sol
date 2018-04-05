pragma solidity ^0.4.21;

/**
 * @title SchedulerInterface
 * @dev The base contract that the higher contracts: BaseScheduler, BlockScheduler and TimestampScheduler all inherit from.
 */
contract SchedulerInterface {
    function schedule(address _toAddress, bytes _callData, uint[8] _uintArgs)
        public payable returns (address);
}
