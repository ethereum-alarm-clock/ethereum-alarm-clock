import "libraries/GroveLib.sol";
import "libraries/AccountingLib.sol";
import "libraries/CallLib.sol";


library SchedulerLib {
    /*
     *  Address: 0x873bf63c898791e57fa66e7b9261ea81df0b8044
     */
    /*
     *  Call Scheduling API
     */
    // Ten minutes into the future.
    uint constant MAX_BLOCKS_IN_FUTURE = 40 + 10 + 255;

    // The minimum gas required to execute a scheduled call on a function that
    // does almost nothing.  This is an approximation and assumes the worst
    // case scenario for gas consumption.
    // 
    // Measured Minimum is closer to 150,000
    uint constant MINIMUM_CALL_GAS = 200000;

    event CallScheduled(address call_address);

    event CallRejected(address indexed schedulerAddress, bytes32 reason);

    uint constant CALL_WINDOW_SIZE = 16;

    function getCallWindowSize() constant returns (uint) {
        return CALL_WINDOW_SIZE;
    }

    function getMinimumGracePeriod() constant returns (uint) {
        return 4 * CALL_WINDOW_SIZE;
    }

    function getMinimumCallGas() constant returns (uint) {
        return MINIMUM_CALL_GAS;
    }

    function getMinimumCallCost(uint basePayment, uint baseFee) constant returns (uint) {
        return 2 * (baseFee + basePayment) + MINIMUM_CALL_GAS * tx.gasprice;
    }

    function scheduleCall(GroveLib.Index storage self, address schedulerAddress, address contractAddress, bytes4 abiSignature, uint targetBlock, uint suggestedGas, uint8 gracePeriod, uint basePayment, uint baseFee, uint endowment) public returns (address) {
        /*
        * Primary API for scheduling a call.
        *
        * - No sooner than MAX_BLOCKS_IN_FUTURE
        * - Grace Period must be longer than the minimum grace period.
        * - msg.value must be >= MIN_GAS * tx.gasprice + 2 * (baseFee + basePayment)
        */
        bytes32 reason;

        if (targetBlock < block.number + MAX_BLOCKS_IN_FUTURE) {
            // Don't allow scheduling further than
            // MAX_BLOCKS_IN_FUTURE
            reason = "TOO_SOON";
        }
        else if (gracePeriod < getMinimumGracePeriod()) {
            reason = "GRACE_TOO_SHORT";
        }
        else if (endowment < 2 * (baseFee + basePayment) + MINIMUM_CALL_GAS * tx.gasprice) {
            reason = "INSUFFICIENT_FUNDS";
        }

        if (reason != 0x0) {
            CallRejected(schedulerAddress, reason);
            AccountingLib.sendRobust(schedulerAddress, endowment);
            return;
        }

        var call = new FutureBlockCall.value(endowment)(schedulerAddress, targetBlock, gracePeriod, contractAddress, abiSignature, suggestedGas, basePayment, baseFee);

        // Put the call into the grove index.
        GroveLib.insert(self, bytes32(address(call)), int(call.targetBlock()));

        CallScheduled(address(call));

        return address(call);
    }
}
