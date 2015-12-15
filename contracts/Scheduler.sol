import "libraries/SchedulerLib.sol";
import "libraries/CallLib.sol";


contract Scheduler {
    /*
     *  Address: 0x321a1e5e0ef137f37eeb5563c987d60ab9dcd8de
     */
    GroveLib.Index callIndex;

    /*
     *  Call Scheduling
     */
    function get_minimum_grace_period() constant returns (uint) {
        return SchedulerLib.get_minimum_grace_period();
    }

    function get_default_payment() constant returns (uint) {
        return 1 ether;
    }

    function get_default_fee() constant returns (uint) {
        return 100 finney;
    }

    function is_known_call(address callAddress) constant returns (bool) {
        return GroveLib.exists(callIndex, bytes32(callAddress));
    }

    function schedule_call(address contract_address, bytes4 abi_signature, uint target_block) public returns (address) {
        return schedule_call(contract_address, abi_signature, target_block, 0, 255, get_default_payment(), get_default_fee());
    }

    function schedule_call(address contract_address, bytes4 abi_signature, uint target_block, uint suggested_gas) public returns (address) {
        return schedule_call(contract_address, abi_signature, target_block, suggested_gas, 255, get_default_payment(), get_default_fee());
    }

    function schedule_call(address contract_address, bytes4 abi_signature, uint target_block, uint suggested_gas, uint8 grace_period) public returns (address) {
        return schedule_call(contract_address, abi_signature, target_block, suggested_gas, grace_period, get_default_payment(), get_default_fee());
    }

    function schedule_call(address contract_address, bytes4 abi_signature, uint target_block, uint suggested_gas, uint8 grace_period, uint base_payment) public returns (address) {
        return schedule_call(contract_address, abi_signature, target_block, suggested_gas, grace_period, base_payment, get_default_fee());
    }

    function schedule_call(address contract_address, bytes4 abi_signature, uint target_block, uint suggested_gas, uint8 grace_period, uint base_payment, uint base_fee) public returns (address) {
        return SchedulerLib.schedule_call(callIndex, msg.sender, contract_address, abi_signature, target_block, suggested_gas, grace_period, base_payment, base_fee, msg.value);
    }

    /*
     *  Next Call API
     */
    function get_call_window_size() constant returns (uint) {
            return SchedulerLib.get_call_window_size();
    }

    function getNextCall(uint blockNumber) constant returns (address) {
            return address(GroveLib.query(callIndex, ">=", int(blockNumber)));
    }

    function get_next_call_sibling(address callAddress) constant returns (address) {
            return address(GroveLib.getNextNode(callIndex, bytes32(callAddress)));
    }
}
