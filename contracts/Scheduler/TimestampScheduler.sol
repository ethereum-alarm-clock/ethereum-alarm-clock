pragma solidity 0.4.24;

import "contracts/Library/RequestScheduleLib.sol";
import "contracts/Scheduler/BaseScheduler.sol";

/**
 * @title TimestampScheduler
 * @dev Top-level contract that exposes the API to the Ethereum Alarm Clock service and passes in timestamp as temporal unit.
 */
contract TimestampScheduler is BaseScheduler {

    /**
     * @dev Constructor
     * @param _factoryAddress Address of the RequestFactory which creates requests for this scheduler.
     */
    constructor(address _factoryAddress, address _feeRecipient) public {
        require(_factoryAddress != 0x0);

        // Default temporal unit is timestamp.
        temporalUnit = RequestScheduleLib.TemporalUnit.Timestamp;

        // Sets the factoryAddress variable found in BaseScheduler contract.
        factoryAddress = _factoryAddress;

        // Sets the fee recipient for these schedulers.
        feeRecipient = _feeRecipient;
    }
}
