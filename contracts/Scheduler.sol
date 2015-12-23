import "libraries/SchedulerLib.sol";
import "libraries/CallLib.sol";


contract Scheduler {
    /*
     *  Address: 0xe109ecb193841af9da3110c80fdd365d1c23be2a
     */
    GroveLib.Index callIndex;

    /*
     *  Call Scheduling
     */
    function getMinimumGracePeriod() constant returns (uint) {
        return SchedulerLib.getMinimumGracePeriod();
    }

    function getDefaultPayment() constant returns (uint) {
        return 1 ether;
    }

    function getDefaultFee() constant returns (uint) {
        return 100 finney;
    }

    function getMinimumCallGas() constant returns (uint) {
        return SchedulerLib.getMinimumCallGas();
    }

    function getMinimumCallCost() constant returns (uint) {
        return getMinimumCallCost(getDefaultPayment(), getDefaultFee());
    }

    function getMinimumCallCost(uint basePayment) constant returns (uint) {
        return getMinimumCallCost(basePayment, getDefaultFee());
    }

    function getMinimumCallCost(uint basePayment, uint baseFee) constant returns (uint) {
        return SchedulerLib.getMinimumCallCost(basePayment, baseFee);
    }

    function isKnownCall(address callAddress) constant returns (bool) {
        return GroveLib.exists(callIndex, bytes32(callAddress));
    }

    function scheduleCall(address contractAddress, bytes4 abiSignature, uint targetBlock) public returns (address) {
        return scheduleCall(contractAddress, abiSignature, targetBlock, 0, 255, getDefaultPayment(), getDefaultFee());
    }

    function scheduleCall(address contractAddress, bytes4 abiSignature, uint targetBlock, uint suggestedGas) public returns (address) {
        return scheduleCall(contractAddress, abiSignature, targetBlock, suggestedGas, 255, getDefaultPayment(), getDefaultFee());
    }

    function scheduleCall(address contractAddress, bytes4 abiSignature, uint targetBlock, uint suggestedGas, uint8 gracePeriod) public returns (address) {
        return scheduleCall(contractAddress, abiSignature, targetBlock, suggestedGas, gracePeriod, getDefaultPayment(), getDefaultFee());
    }

    function scheduleCall(address contractAddress, bytes4 abiSignature, uint targetBlock, uint suggestedGas, uint8 gracePeriod, uint basePayment) public returns (address) {
        return scheduleCall(contractAddress, abiSignature, targetBlock, suggestedGas, gracePeriod, basePayment, getDefaultFee());
    }

    function scheduleCall(address contractAddress, bytes4 abiSignature, uint targetBlock, uint suggestedGas, uint8 gracePeriod, uint basePayment, uint baseFee) public returns (address) {
        return SchedulerLib.scheduleCall(callIndex, msg.sender, contractAddress, abiSignature, targetBlock, suggestedGas, gracePeriod, basePayment, baseFee, msg.value);
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
