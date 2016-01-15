import "libraries/GroveLib.sol";
import "libraries/AccountingLib.sol";
import "libraries/CallLib.sol";


library SchedulerLib {
    /*
     *  Address: 0xac0500b26e61a8b26700289d9cd326adbc17be0e
     */
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

    // The maximum possible depth that stack depth checking can achieve.
    uint constant MAXIMUM_STACK_CHECK = 339;

    event CallScheduled(address call_address);

    event CallRejected(address indexed schedulerAddress, bytes32 reason);

    uint constant CALL_WINDOW_SIZE = 16;

    function getMaximumStackCheck() constant returns (uint) {
        return MAXIMUM_STACK_CHECK;
    }

    function getCallWindowSize() constant returns (uint) {
        return CALL_WINDOW_SIZE;
    }

    function getMinimumGracePeriod() constant returns (uint) {
        return 2 * CALL_WINDOW_SIZE;
    }

    function getMinimumCallGas() constant returns (uint) {
        return MINIMUM_CALL_GAS;
    }

    function getMinimumCallCost(uint basePayment, uint baseDonation) constant returns (uint) {
        return 2 * (baseDonation + basePayment) + MINIMUM_CALL_GAS * tx.gasprice;
    }

    struct CallConfig {
        address schedulerAddress;
        address contractAddress;
        bytes4 abiSignature;
        bytes callData;
        uint8 gracePeriod;
        uint16 requiredStackDepth;
        uint targetBlock;
        uint requiredGas;
        uint basePayment;
        uint baseDonation;
        uint endowment;
    }

    function scheduleCall(GroveLib.Index storage self,
                          address schedulerAddress,
                          address contractAddress,
                          bytes4 abiSignature,
                          bytes callData,
                          uint8 gracePeriod,
                          uint16 requiredStackDepth,
                          uint targetBlock,
                          uint requiredGas,
                          uint basePayment,
                          uint baseDonation,
                          uint endowment) public returns (address) {
        CallConfig memory callConfig = CallConfig({
            schedulerAddress: schedulerAddress,
            contractAddress: contractAddress,
            abiSignature: abiSignature,
            callData: callData,
            gracePeriod: gracePeriod,
            requiredStackDepth: requiredStackDepth,
            targetBlock: targetBlock,
            requiredGas: requiredGas,
            basePayment: basePayment,
            baseDonation: baseDonation,
            endowment: endowment,
        });
        return _scheduleCall(self, callConfig);
    }

    function _scheduleCall(GroveLib.Index storage self,
                          CallConfig memory callConfig) internal returns (address) {
        /*
        * Primary API for scheduling a call.
        *
        * - No sooner than MAX_BLOCKS_IN_FUTURE
        * - Grace Period must be longer than the minimum grace period.
        * - msg.value must be >= MIN_GAS * tx.gasprice + 2 * (baseDonation + basePayment)
        */
        bytes32 reason;

        if (callConfig.targetBlock < block.number + MAX_BLOCKS_IN_FUTURE) {
            // Don't allow scheduling further than
            // MAX_BLOCKS_IN_FUTURE
            reason = "TOO_SOON";
        }
        else if (callConfig.requiredStackDepth > MAXIMUM_STACK_CHECK) {
            // Cannot require stack depth greater than MAXIMUM_STACK_CHECK
            reason = "STACK_CHECK_TOO_LARGE";
        }
        else if (callConfig.gracePeriod < getMinimumGracePeriod()) {
            reason = "GRACE_TOO_SHORT";
        }
        else if (callConfig.endowment < 2 * (callConfig.baseDonation + callConfig.basePayment) + MINIMUM_CALL_GAS * tx.gasprice) {
            reason = "INSUFFICIENT_FUNDS";
        }

        if (reason != 0x0) {
            CallRejected(callConfig.schedulerAddress, reason);
            AccountingLib.sendRobust(callConfig.schedulerAddress, callConfig.endowment);
            return;
        }

        var call = new FutureBlockCall.value(callConfig.endowment)(
                callConfig.schedulerAddress,
                callConfig.targetBlock,
                callConfig.gracePeriod,
                callConfig.contractAddress,
                callConfig.abiSignature,
                callConfig.callData,
                callConfig.requiredGas,
                callConfig.requiredStackDepth,
                callConfig.basePayment,
                callConfig.baseDonation
        );

        // Put the call into the grove index.
        GroveLib.insert(self, bytes32(address(call)), int(call.targetBlock()));

        CallScheduled(address(call));

        return address(call);
    }
}
