import "libraries/SchedulerLib.sol";
import "libraries/CallLib.sol";


contract Scheduler {
    /*
     *  Address: 0xe109ecb193841af9da3110c80fdd365d1c23be2a
     */

    // callIndex tracks the ordering of scheduled calls based on their block numbers.
    GroveLib.Index callIndex;

    // callOrigin tracks the origin scheduler contract for each scheduled call.
    mapping (address => address) callOrigin;

    uint constant CALL_API_VERSION = 1;

    function callAPIVersion() constant returns (uint) {
        return CALL_API_VERSION;
    }

    /*
     *  Call Scheduling
     */
    function getMinimumGracePeriod() constant returns (uint) {
        return SchedulerLib.getMinimumGracePeriod();
    }

    // TODO: this needs to be a reasonable number.  too high right now.
    // Based on a gas price of 50,000 lovelace targeting 1 ether
    uint constant DEFAULT_PAYMENT_GAS = 20000000;

    function getDefaultPayment() constant returns (uint) {
        return tx.gasprice * DEFAULT_PAYMENT_GAS;
    }

    // Based on a gas price of 50,000 lovelace targeting 100 finney
    uint constant DEFAULT_DONATION_GAS = 2000000;

    function getDefaultDonation() constant returns (uint) {
        return tx.gasprice * DEFAULT_DONATION_GAS;
    }

    function getMinimumCallGas() constant returns (uint) {
        return SchedulerLib.getMinimumCallGas();
    }

    function getMinimumEndowment() constant returns (uint) {
        return SchedulerLib.getMinimumEndowment(getDefaultPayment(), getDefaultDonation(), 0, getDefaultRequiredGas());
    }

    function getMinimumEndowment(uint basePayment) constant returns (uint) {
        return SchedulerLib.getMinimumEndowment(basePayment, getDefaultDonation(), 0, getDefaultRequiredGas());
    }

    function getMinimumEndowment(uint basePayment, uint baseDonation) constant returns (uint) {
        return SchedulerLib.getMinimumEndowment(basePayment, baseDonation, 0, getDefaultRequiredGas());
    }

    function getMinimumEndowment(uint basePayment, uint baseDonation, uint callValue) constant returns (uint) {
        return SchedulerLib.getMinimumEndowment(basePayment, baseDonation, callValue, getDefaultRequiredGas());
    }

    function getMinimumEndowment(uint basePayment, uint baseDonation, uint callValue, uint requiredGas) constant returns (uint) {
        return SchedulerLib.getMinimumEndowment(basePayment, baseDonation, callValue, requiredGas);
    }

    function isKnownCall(address callAddress) constant returns (bool) {
        return GroveLib.exists(callIndex, bytes32(callAddress));
    }

    function getFirstSchedulableBlock() constant returns (uint) {
        return block.number + MIN_BLOCKS_IN_FUTURE;
    }

    function getDefaultRequiredStackDepth() constant returns (uint16) {
        return SchedulerLib.getMinimumStackCheck();
    }

    function getMinimumStackCheck() constant returns (uint16) {
        return SchedulerLib.getMinimumStackCheck();
    }

    function getMaximumStackCheck() constant returns (uint16) {
        return SchedulerLib.getMaximumStackCheck();
    }

    function getDefaultRequiredGas() constant returns (uint) {
        return SchedulerLib.getMinimumCallGas();
    }

    // Ten minutes into the future (duplicated from SchedulerLib)
    uint constant MIN_BLOCKS_IN_FUTURE = 40;
    bytes constant EMPTY_CALL_DATA = "";
    uint16 constant DEFAULT_REQUIRED_STACK_DEPTH = 10;
    uint8 constant DEFAULT_GRACE_PERIOD = 255;
    uint constant DEFAULT_CALL_VALUE = 0;
    bytes4 constant DEFAULT_FN_SIGNATURE = 0x0000;

    function scheduleCall() public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            DEFAULT_FN_SIGNATURE, EMPTY_CALL_DATA, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, getFirstSchedulableBlock(), getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(uint targetBlock) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            DEFAULT_FN_SIGNATURE, EMPTY_CALL_DATA, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, targetBlock, getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes callData) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            DEFAULT_FN_SIGNATURE, callData, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, getFirstSchedulableBlock(), getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes4 abiSignature,
                          bytes callData) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            abiSignature, callData, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, getFirstSchedulableBlock(), getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes4 abiSignature) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            abiSignature, EMPTY_CALL_DATA, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, getFirstSchedulableBlock(), getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            DEFAULT_FN_SIGNATURE, EMPTY_CALL_DATA, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, getFirstSchedulableBlock(), getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, EMPTY_CALL_DATA, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, getFirstSchedulableBlock(), getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          uint callValue,
                          bytes4 abiSignature) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, EMPTY_CALL_DATA, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            callValue, getFirstSchedulableBlock(), getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          bytes callData) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, callData, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, getFirstSchedulableBlock(), getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          uint callValue,
                          bytes callData) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, callData, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            callValue, getFirstSchedulableBlock(), getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(uint callValue,
                          address contractAddress) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            DEFAULT_FN_SIGNATURE, EMPTY_CALL_DATA, DEFAULT_GRACE_PERIOD,DEFAULT_REQUIRED_STACK_DEPTH,
            callValue, getFirstSchedulableBlock(), getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          uint targetBlock) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            DEFAULT_FN_SIGNATURE, EMPTY_CALL_DATA, DEFAULT_GRACE_PERIOD,DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, targetBlock, getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          uint targetBlock,
                          uint callValue) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            DEFAULT_FN_SIGNATURE, EMPTY_CALL_DATA, DEFAULT_GRACE_PERIOD,DEFAULT_REQUIRED_STACK_DEPTH,
            callValue, targetBlock, getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes4 abiSignature,
                          uint targetBlock) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            abiSignature, EMPTY_CALL_DATA, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, targetBlock, getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          uint targetBlock) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, EMPTY_CALL_DATA, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, targetBlock, getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes4 abiSignature,
                          bytes callData,
                          uint targetBlock) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            abiSignature, callData, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, targetBlock, getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          bytes callData,
                          uint targetBlock) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, callData, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, targetBlock, getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          uint callValue,
                          bytes callData,
                          uint targetBlock) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, callData, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            callValue, targetBlock, getDefaultRequiredGas(), getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes4 abiSignature,
                          uint targetBlock,
                          uint requiredGas) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            abiSignature, EMPTY_CALL_DATA, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          uint targetBlock,
                          uint requiredGas) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, EMPTY_CALL_DATA, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes4 abiSignature,
                          bytes callData,
                          uint targetBlock,
                          uint requiredGas) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            abiSignature, callData, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          bytes callData,
                          uint targetBlock,
                          uint requiredGas) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, callData, DEFAULT_GRACE_PERIOD, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes4 abiSignature,
                          uint targetBlock,
                          uint requiredGas,
                          uint8 gracePeriod) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            abiSignature, EMPTY_CALL_DATA, gracePeriod, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          uint callValue,
                          bytes4 abiSignature,
                          uint targetBlock,
                          uint requiredGas,
                          uint8 gracePeriod) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, EMPTY_CALL_DATA, gracePeriod, DEFAULT_REQUIRED_STACK_DEPTH,
            callValue, targetBlock, requiredGas, getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          uint targetBlock,
                          uint requiredGas,
                          uint8 gracePeriod) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, EMPTY_CALL_DATA, gracePeriod, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          bytes callData,
                          uint targetBlock,
                          uint requiredGas,
                          uint8 gracePeriod) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, callData, gracePeriod, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, getDefaultPayment(), getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes4 abiSignature,
                          uint targetBlock,
                          uint requiredGas,
                          uint8 gracePeriod,
                          uint basePayment) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            abiSignature, EMPTY_CALL_DATA, gracePeriod, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, basePayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          uint callValue,
                          bytes4 abiSignature,
                          uint targetBlock,
                          uint requiredGas,
                          uint8 gracePeriod,
                          uint basePayment) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, EMPTY_CALL_DATA, gracePeriod, DEFAULT_REQUIRED_STACK_DEPTH,
            callValue, targetBlock, requiredGas, basePayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          uint targetBlock,
                          uint requiredGas,
                          uint8 gracePeriod,
                          uint basePayment) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, EMPTY_CALL_DATA, gracePeriod, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, basePayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes4 abiSignature,
                          bytes callData,
                          uint targetBlock,
                          uint requiredGas,
                          uint8 gracePeriod,
                          uint basePayment) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            abiSignature, callData, gracePeriod, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, basePayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          bytes callData,
                          uint8 gracePeriod,
                          uint[4] uints) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, callData, gracePeriod, DEFAULT_REQUIRED_STACK_DEPTH,
            // callValue, targetBlock, requiredGas, basePayment
            uints[0], uints[1], uints[2], uints[3], getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          bytes callData,
                          uint targetBlock,
                          uint requiredGas,
                          uint8 gracePeriod,
                          uint basePayment) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, callData, gracePeriod, DEFAULT_REQUIRED_STACK_DEPTH,
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, basePayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes4 abiSignature,
                          bytes callData,
                          uint16 requiredStackDepth,
                          uint8 gracePeriod,
                          uint callValue,
                          uint targetBlock,
                          uint requiredGas,
                          uint basePayment,
                          uint baseDonation) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            abiSignature, callData, gracePeriod, requiredStackDepth,
            callValue, targetBlock, requiredGas, basePayment, baseDonation, msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          bytes callData,
                          uint16 requiredStackDepth,
                          uint8 gracePeriod,
                          uint[5] uints) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            [msg.sender, contractAddress],
            abiSignature, callData, gracePeriod, requiredStackDepth,
            // callValue, targetBlock, requiredGas, basePayment, baseDonation
            [uints[0], uints[1], uints[2], uints[3], uints[4], msg.value]
        );
    }

    /*
     *  Next Call API
     */
    function getCallWindowSize() constant returns (uint) {
            return SchedulerLib.getCallWindowSize();
    }

    function getNextCall(uint blockNumber) constant returns (address) {
            return address(GroveLib.query(callIndex, ">=", int(blockNumber)));
    }

    function getNextCallSibling(address callAddress) constant returns (address) {
            return address(GroveLib.getNextNode(callIndex, bytes32(callAddress)));
    }
}
