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
    function version() constant returns (uint16, uint16, uint16) {
        return (0, 7, 0);
    }

    // Ten minutes into the future.
    uint constant MIN_BLOCKS_IN_FUTURE = 10;

    // max of uint8
    uint8 constant DEFAULT_GRACE_PERIOD = 255;

    // The minimum gas required to execute a scheduled call on a function that
    // does almost nothing.  This is an approximation and assumes the worst
    // case scenario for gas consumption.
    // 
    // Measured Minimum is closer to 115,000
    uint constant MINIMUM_CALL_GAS = 130000;

    // The minimum depth required to execute a call.
    uint16 constant MINIMUM_STACK_CHECK = 10;

    // The maximum possible depth that stack depth checking can achieve.
    // Actual check limit is 1021.  Actual call limit is 1021
    uint16 constant MAXIMUM_STACK_CHECK = 1000;

    event CallScheduled(address call_address);

    event CallRejected(address indexed schedulerAddress, bytes32 reason);

    uint constant CALL_WINDOW_SIZE = 16;

    function getMinimumStackCheck() constant returns (uint16) {
        return MINIMUM_STACK_CHECK;
    }

    function getMaximumStackCheck() constant returns (uint16) {
        return MAXIMUM_STACK_CHECK;
    }

    function getCallWindowSize() constant returns (uint) {
        return CALL_WINDOW_SIZE;
    }

    function getMinimumGracePeriod() constant returns (uint) {
        return 2 * CALL_WINDOW_SIZE;
    }

    function getDefaultGracePeriod() constant returns (uint8) {
        return DEFAULT_GRACE_PERIOD;
    }

    function getMinimumCallGas() constant returns (uint) {
        return MINIMUM_CALL_GAS;
    }

    function getMaximumCallGas() constant returns (uint) {
        return block.gaslimit - getMinimumCallGas();
    }

    function getMinimumCallCost(uint basePayment, uint baseDonation) constant returns (uint) {
        return 2 * (baseDonation + basePayment) + MINIMUM_CALL_GAS * tx.gasprice;
    }

    function getFirstSchedulableBlock() constant returns (uint) {
        return block.number + MIN_BLOCKS_IN_FUTURE;
    }

    function getMinimumEndowment(uint basePayment,
                                 uint baseDonation,
                                 uint callValue,
                                 uint requiredGas) constant returns (uint endowment) {
            endowment += tx.gasprice * requiredGas;
            endowment += 2 * (basePayment + baseDonation);
            endowment += callValue;

            return endowment;
    }

    struct CallConfig {
        address schedulerAddress;
        address contractAddress;
        bytes4 abiSignature;
        bytes callData;
        uint callValue;
        uint8 gracePeriod;
        uint16 requiredStackDepth;
        uint targetBlock;
        uint requiredGas;
        uint basePayment;
        uint baseDonation;
        uint endowment;
    }

    function scheduleCall(GroveLib.Index storage callIndex,
                          address schedulerAddress,
                          address contractAddress,
                          bytes4 abiSignature,
                          bytes callData,
                          uint8 gracePeriod,
                          uint16 requiredStackDepth,
                          uint callValue,
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
            callValue: callValue,
            targetBlock: targetBlock,
            requiredGas: requiredGas,
            basePayment: basePayment,
            baseDonation: baseDonation,
            endowment: endowment,
        });
        return _scheduleCall(callIndex, callConfig);
    }

    function scheduleCall(GroveLib.Index storage callIndex,
                          address[2] addresses,
                          bytes4 abiSignature,
                          bytes callData,
                          uint8 gracePeriod,
                          uint16 requiredStackDepth,
                          uint[6] uints) public returns (address) {
        CallConfig memory callConfig = CallConfig({
            schedulerAddress: addresses[0],
            contractAddress: addresses[1],
            abiSignature: abiSignature,
            callData: callData,
            gracePeriod: gracePeriod,
            requiredStackDepth: requiredStackDepth,
            callValue: uints[0],
            targetBlock: uints[1],
            requiredGas: uints[2],
            basePayment: uints[3],
            baseDonation: uints[4],
            endowment: uints[5],
        });
        return _scheduleCall(callIndex, callConfig);

    }

    function _scheduleCall(GroveLib.Index storage callIndex, CallConfig memory callConfig) internal returns (address) {
        /*
        * Primary API for scheduling a call.
        *
        * - No sooner than MIN_BLOCKS_IN_FUTURE
        * - Grace Period must be longer than the minimum grace period.
        * - msg.value must be >= MIN_GAS * tx.gasprice + 2 * (baseDonation + basePayment)
        */
        bytes32 reason;

        if (callConfig.targetBlock < block.number + MIN_BLOCKS_IN_FUTURE) {
            // Don't allow scheduling further than
            // MIN_BLOCKS_IN_FUTURE
            reason = "TOO_SOON";
        }
        else if (getMinimumStackCheck() > callConfig.requiredStackDepth || callConfig.requiredStackDepth > getMaximumStackCheck()) {
            // Cannot require stack depth greater than MAXIMUM_STACK_CHECK or
            // less than MINIMUM_STACK_CHECK
            reason = "STACK_CHECK_OUT_OF_RANGE";
        }
        else if (callConfig.gracePeriod < getMinimumGracePeriod()) {
            reason = "GRACE_TOO_SHORT";
        }
        else if (callConfig.requiredGas < getMinimumCallGas() || callConfig.requiredGas > getMaximumCallGas()) {
            reason = "REQUIRED_GAS_OUT_OF_RANGE";
        }
        else if (callConfig.endowment < getMinimumEndowment(callConfig.basePayment, callConfig.baseDonation, callConfig.callValue, callConfig.requiredGas)) {
            reason = "INSUFFICIENT_FUNDS";
        }

        if (reason != 0x0) {
            CallRejected(callConfig.schedulerAddress, reason);
            AccountingLib.sendRobust(callConfig.schedulerAddress, callConfig.endowment);
            return;
        }

        var call = (new FutureBlockCall).value(callConfig.endowment)(
                callConfig.schedulerAddress,
                callConfig.targetBlock,
                callConfig.gracePeriod,
                callConfig.contractAddress,
                callConfig.abiSignature,
                callConfig.callData,
                callConfig.callValue,
                callConfig.requiredGas,
                callConfig.requiredStackDepth,
                callConfig.basePayment,
                callConfig.baseDonation
        );

        // Put the call into the grove index.
        GroveLib.insert(callIndex, bytes32(address(call)), int(call.targetBlock()));

        CallScheduled(address(call));

        return address(call);
    }
}
