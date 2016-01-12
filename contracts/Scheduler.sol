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

    function getDefaultPayment() constant returns (uint) {
        return 1 ether;
    }

    function getDefaultDonation() constant returns (uint) {
        return 100 finney;
    }

    function getMinimumCallGas() constant returns (uint) {
        return SchedulerLib.getMinimumCallGas();
    }

    function getMinimumCallCost() constant returns (uint) {
        return getMinimumCallCost(getDefaultPayment(), getDefaultDonation());
    }

    function getMinimumCallCost(uint basePayment) constant returns (uint) {
        return getMinimumCallCost(basePayment, getDefaultDonation());
    }

    function getMinimumCallCost(uint basePayment, uint baseDonation) constant returns (uint) {
        return SchedulerLib.getMinimumCallCost(basePayment, baseDonation);
    }

    function isKnownCall(address callAddress) constant returns (bool) {
        return GroveLib.exists(callIndex, bytes32(callAddress));
    }

    function scheduleCall(uint targetBlock) public returns (address) {
        bytes memory callData;
        return SchedulerLib.scheduleCall(callIndex, msg.sender, msg.sender, 0x0, callData, targetBlock, 0, 255, getDefaultPayment(), getDefaultDonation(), msg.value);
    }

    function scheduleCall(address contractAddress,
                          uint targetBlock) public returns (address) {
        bytes memory callData;
        return SchedulerLib.scheduleCall(callIndex, msg.sender, contractAddress, 0x0, callData, targetBlock, 0, 255, getDefaultPayment(), getDefaultDonation(), msg.value);
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          uint targetBlock) public returns (address) {
        bytes memory callData;
        return SchedulerLib.scheduleCall(callIndex, msg.sender, contractAddress, abiSignature, callData, targetBlock, 0, 255, getDefaultPayment(), getDefaultDonation(), msg.value);
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          bytes callData,
                          uint targetBlock) public returns (address) {
        return SchedulerLib.scheduleCall(callIndex, msg.sender, contractAddress, abiSignature, callData, targetBlock, 0, 255, getDefaultPayment(), getDefaultDonation(), msg.value);
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          uint targetBlock,
                          uint suggestedGas) public returns (address) {
        bytes memory callData;
        return SchedulerLib.scheduleCall(callIndex, msg.sender, contractAddress, abiSignature, callData, targetBlock, suggestedGas, 255, getDefaultPayment(), getDefaultDonation(), msg.value);
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          bytes callData,
                          uint targetBlock,
                          uint suggestedGas) public returns (address) {
        return SchedulerLib.scheduleCall(callIndex, msg.sender, contractAddress, abiSignature, callData, targetBlock, suggestedGas, 255, getDefaultPayment(), getDefaultDonation(), msg.value);
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          uint targetBlock,
                          uint suggestedGas,
                          uint8 gracePeriod) public returns (address) {
        bytes memory callData;
        return SchedulerLib.scheduleCall(callIndex, msg.sender, contractAddress, abiSignature, callData, targetBlock, suggestedGas, gracePeriod, getDefaultPayment(), getDefaultDonation(), msg.value);
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          bytes callData,
                          uint targetBlock,
                          uint suggestedGas,
                          uint8 gracePeriod) public returns (address) {
        return SchedulerLib.scheduleCall(callIndex, msg.sender, contractAddress, abiSignature, callData, targetBlock, suggestedGas, gracePeriod, getDefaultPayment(), getDefaultDonation(), msg.value);
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          uint targetBlock,
                          uint suggestedGas,
                          uint8 gracePeriod,
                          uint basePayment) public returns (address) {
        bytes memory callData;
        return SchedulerLib.scheduleCall(callIndex, msg.sender, contractAddress, abiSignature, callData, targetBlock, suggestedGas, gracePeriod, basePayment, getDefaultDonation(), msg.value);
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          bytes callData,
                          uint targetBlock,
                          uint suggestedGas,
                          uint8 gracePeriod,
                          uint basePayment) public returns (address) {
        return SchedulerLib.scheduleCall(callIndex, msg.sender, contractAddress, abiSignature, callData, targetBlock, suggestedGas, gracePeriod, basePayment, getDefaultDonation(), msg.value);
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          bytes callData,
                          uint targetBlock,
                          uint suggestedGas,
                          uint8 gracePeriod,
                          uint basePayment,
                          uint baseDonation) public returns (address) {
        return SchedulerLib.scheduleCall(callIndex, msg.sender, contractAddress, abiSignature, callData, targetBlock, suggestedGas, gracePeriod, basePayment, baseDonation, msg.value);
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
