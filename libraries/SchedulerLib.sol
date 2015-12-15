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
    uint constant MAX_BLOCKS_IN_FUTURE = 40;

    // The minimum gas required to execute a scheduled call on a function that
    // does almost nothing.  This is an approximation and assumes the worst
    // case scenario for gas consumption.
    // 
    // Measured Minimum is closer to 150,000
    uint constant MINIMUM_CALL_GAS = 200000;

    event CallScheduled(address call_address);

    event CallRejected(address indexed scheduler_address, bytes32 reason);

    uint constant CALL_WINDOW_SIZE = 16;

    function get_call_window_size() constant returns (uint) {
        return CALL_WINDOW_SIZE;
    }

    function get_minimum_grace_period() constant returns (uint) {
        return 4 * CALL_WINDOW_SIZE;
    }

    function getMinimumCallGas() constant returns (uint) {
        return MINIMUM_CALL_GAS;
    }

    function get_minimum_call_cost(uint base_payment) constant returns (uint) {
        return get_minimum_call_cost(base_payment, base_payment);
    }

    function get_minimum_call_cost(uint base_payment, uint base_fee) constant returns (uint) {
        return 2 * (base_fee + base_payment) + MINIMUM_CALL_GAS * tx.gasprice;
    }

    function schedule_call(GroveLib.Index storage self, address scheduler_address, address contractAddress, bytes4 abi_signature, uint target_block, uint suggested_gas, uint8 grace_period, uint base_payment, uint base_fee, uint endowment) public returns (address) {
        /*
        * Primary API for scheduling a call.
        *
        * - No sooner than MAX_BLOCKS_IN_FUTURE
        * - Grace Period must be longer than the minimum grace period.
        * - msg.value must be >= MIN_GAS * tx.gasprice + 2 * (base_fee + base_payment)
        */
        bytes32 reason;

        if (target_block < block.number + MAX_BLOCKS_IN_FUTURE) {
            // Don't allow scheduling further than
            // MAX_BLOCKS_IN_FUTURE
            reason = "TOO_SOON";
        }
        else if (grace_period < get_minimum_grace_period()) {
            reason = "GRACE_TOO_SHORT";
        }
        else if (endowment < 2 * (base_fee + base_payment) + MINIMUM_CALL_GAS * tx.gasprice) {
            reason = "INSUFFICIENT_FUNDS";
        }

        if (reason != 0x0) {
            CallRejected(scheduler_address, reason);
            AccountingLib.sendRobust(scheduler_address, endowment);
            return;
        }

        var call = new FutureBlockCall.value(endowment)(scheduler_address, target_block, grace_period, contractAddress, abi_signature, suggested_gas, base_payment, base_fee);

        // Put the call into the grove index.
        GroveLib.insert(self, bytes32(address(call)), int(call.target_block()));

        CallScheduled(address(call));

        return address(call);
    }
}
