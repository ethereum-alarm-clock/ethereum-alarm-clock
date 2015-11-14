import "libraries/GroveLib.sol";
import "libraries/AccountingLib.sol";
import "libraries/CallLib.sol";


library SchedulerLib {
    /*
     *  Address: 0x873bf63c898791e57fa66e7b9261ea81df0b8044
     */
    struct CallDatabase {
        GroveLib.Index callIndex;

        AccountingLib.Bank gasBank;
    }

    // The number of blocks that each caller in the pool has to complete their
    // call.
    uint constant CALL_WINDOW_SIZE = 16;

    /*
     *  Call Scheduling API
     */
    // Ten minutes into the future.
    uint constant MAX_BLOCKS_IN_FUTURE = 40;

    // The minimum gas required to execute a scheduled call on a function that
    // does almost nothing.  This is an approximation and assumes the worst
    // case scenario for gas consumption.
    // 
    // Measured Minimum is closer to 150,000
    uint constant MINIMUM_CALL_GAS = 200000;

    event CallScheduled(address callAddress);

    event CallRejected(address indexed schedulerAddress, bytes32 reason);

    function getCallWindowSize() constant returns (uint) {
        return CALL_WINDOW_SIZE;
    }

    function getMinimumGracePeriod() constant returns (uint) {
        return 4 * CALL_WINDOW_SIZE;
    }

    function getMinimumCallGas() constant returns (uint) {
        return MINIMUM_CALL_GAS;
    }

    function getMinimumCallCost(uint basePayment) constant returns (uint) {
        return getMinimumCallCost(basePayment, basePayment);
    }

    function getMinimumCallCost(uint basePayment, uint baseFee) constant returns (uint) {
        return 2 * (baseFee + basePayment) + MINIMUM_CALL_GAS * tx.gasprice;
    }

    function isKnownCall(CallDatabase storage self, address callAddress) constant returns (bool) {
        return GroveLib.exists(self.callIndex, bytes32(callAddress));
    }

    function scheduleCall(CallDatabase storage self, address schedulerAddress, address contractAddress, bytes4 abiSignature, uint targetBlock, uint suggestedGas, uint8 gracePeriod, uint basePayment, uint baseFee, uint endowment) public returns (address) {
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
        GroveLib.insert(self.callIndex, bytes32(address(call)), int(call.targetBlock()));

        CallScheduled(address(call));

        return address(call);
    }

    function execute(CallDatabase storage self, uint startGas, address callAddress, address executor) {
        if (!isKnownCall(self, callAddress)) {
                CallLib.CallAborted(executor, "UNKNOWN_ADDRESS");
                return;
        }

        FutureBlockCall call = FutureBlockCall(callAddress);

        if (!call.isAlive()) {
                CallLib.CallAborted(executor, "SUICIDED_ALREADY");
                return;
        }
        
        bool isDesignated;
        address designatedCaller;

        (isDesignated, designatedCaller) = getDesignatedCaller(self, call.targetBlock(), call.targetBlock() + call.gracePeriod(), block.number);
        if (isDesignated && designatedCaller != 0x0 && designatedCaller != executor) {
                // Wrong caller
                CallLib.CallAborted(executor, "WRONG_CALLER");
                return;
        }

        if (!call.beforeExecute(executor)) {
                return;
        }

        if (isDesignated) {
            uint blockWindow = (block.number - call.targetBlock()) / getCallWindowSize();
            if (blockWindow > 0) {
                // Someone missed their call so this caller
                // gets to claim their bond for picking up
                // their slack.
                awardMissedBlockBonus(self, executor, callAddress);
            }
        }
        call.execute(startGas, executor);
    }
}
