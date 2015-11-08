import "libraries/SchedulerLib.sol";
import "libraries/CallLib.sol";
import "libraries/ResourcePoolLib.sol";


contract Scheduler {
    /*
     *  Address: 0x321a1e5e0ef137f37eeb5563c987d60ab9dcd8de
     *
     *  Constructor
     *
     *  - sets up relays
     *  - configures the caller pool.
     */
    function Scheduler() {
            callDatabase.callerPool.freezePeriod = 80;
            callDatabase.callerPool.rotationDelay = 80;
            callDatabase.callerPool.overlapSize = 256;
    }

    SchedulerLib.CallDatabase callDatabase;

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

    function isKnownCall(address callAddress) constant returns (bool) {
        return SchedulerLib.isKnownCall(callDatabase, callAddress);
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
        return SchedulerLib.scheduleCall(callDatabase, msg.sender, contractAddress, abiSignature, targetBlock, suggestedGas, gracePeriod, basePayment, baseFee, msg.value);
    }

    /*
     *  Call Execution
     */
    function execute(address callAddress) public {
        uint startGas = msg.gas;

        SchedulerLib.execute(callDatabase, startGas, callAddress, msg.sender);
    }

    /*
     *  Caller Pool Bonding
     */
    function getMinimumBond() constant returns (uint) {
        return SchedulerLib.getMinimumBond();
    }

    function depositBond() public {
        ResourcePoolLib.addToBond(callDatabase.callerPool, msg.sender, msg.value);
    }

    function withdrawBond(uint value) public {
        ResourcePoolLib.withdrawBond(callDatabase.callerPool, msg.sender, value, getMinimumBond());
    }

    function getBondBalance() constant returns (uint) {
        return getBondBalance(msg.sender);
    }

    function getBondBalance(address callerAddress) constant returns (uint) {
        return callDatabase.callerPool.bonds[callerAddress];
    }

    /*
     *  Pool Management
     */
    function getGenerationForCall(address callAddress) constant returns (uint) {
            var call = FutureBlockCall(callAddress);
            return ResourcePoolLib.getGenerationForWindow(callDatabase.callerPool, call.targetBlock(), call.targetBlock() + call.gracePeriod());
    }

    function getGenerationSize(uint generationId) constant returns (uint) {
            return callDatabase.callerPool.generations[generationId].members.length;
    }

    function getGenerationStartAt(uint generationId) constant returns (uint) {
            return callDatabase.callerPool.generations[generationId].startAt;
    }

    function getGenerationEndAt(uint generationId) constant returns (uint) {
            return callDatabase.callerPool.generations[generationId].endAt;
    }

    function getCurrentGenerationId() constant returns (uint) {
            return ResourcePoolLib.getCurrentGenerationId(callDatabase.callerPool);
    }

    function getNextGenerationId() constant returns (uint) {
            return ResourcePoolLib.getNextGenerationId(callDatabase.callerPool);
    }

    function isInPool() constant returns (bool) {
            return ResourcePoolLib.isInPool(callDatabase.callerPool, msg.sender);
    }

    function isInPool(address callerAddress) constant returns (bool) {
            return ResourcePoolLib.isInPool(callDatabase.callerPool, callerAddress);
    }

    function isInGeneration(uint generationId) constant returns (bool) {
            return isInGeneration(msg.sender, generationId);
    }

    function isInGeneration(address callerAddress, uint generationId) constant returns (bool) {
            return ResourcePoolLib.isInGeneration(callDatabase.callerPool, callerAddress, generationId);
    }

    /*
     *  Pool Meta information
     */
    function getPoolFreezePeriod() constant returns (uint) {
            return callDatabase.callerPool.freezePeriod;
    }

    function getPoolOverlapSize() constant returns (uint) {
            return callDatabase.callerPool.overlapSize;
    }

    function getPoolRotationDelay() constant returns (uint) {
            return callDatabase.callerPool.rotationDelay;
    }

    /*
     *  Pool Membership
     */
    function canEnterPool() constant returns (bool) {
            return ResourcePoolLib.canEnterPool(callDatabase.callerPool, msg.sender, getMinimumBond());
    }

    function canEnterPool(address callerAddress) constant returns (bool) {
            return ResourcePoolLib.canEnterPool(callDatabase.callerPool, callerAddress, getMinimumBond());
    }

    function canExitPool() constant returns (bool) {
            return ResourcePoolLib.canExitPool(callDatabase.callerPool, msg.sender);
    }

    function canExitPool(address callerAddress) constant returns (bool) {
            return ResourcePoolLib.canExitPool(callDatabase.callerPool, callerAddress);
    }

    function enterPool() public {
            uint generationId = ResourcePoolLib.enterPool(callDatabase.callerPool, msg.sender, getMinimumBond());
            ResourcePoolLib.AddedToGeneration(msg.sender, generationId);
    }

    function exitPool() public {
            uint generationId = ResourcePoolLib.exitPool(callDatabase.callerPool, msg.sender);
            ResourcePoolLib.RemovedFromGeneration(msg.sender, generationId);
    }

    /*
     *  Next Call API
     */
    function getCallWindowSize() constant returns (uint) {
            // TODO: is this function needed
            return SchedulerLib.getCallWindowSize();
    }

    function getGenerationIdForCall(address callAddress) constant returns (uint) {
            // TODO: is this function needed
            return SchedulerLib.getGenerationIdForCall(callDatabase, callAddress);
    }

    function getDesignatedCaller(address callAddress, uint blockNumber) constant returns (bool, address) {
            // TODO: is this function needed
            var call = FutureBlockCall(callAddress);
            return SchedulerLib.getDesignatedCaller(callDatabase, call.targetBlock(), call.targetBlock() + call.gracePeriod(), blockNumber);
    }

    function getNextCall(uint blockNumber) constant returns (address) {
            return address(GroveLib.query(callDatabase.callIndex, ">=", int(blockNumber)));
    }

    function getNextCallSibling(address callAddress) constant returns (address) {
            return address(GroveLib.getNextNode(callDatabase.callIndex, bytes32(callAddress)));
    }
}
