import "libraries/SchedulerLib.sol";
import "libraries/CallLib.sol";


contract Scheduler {
    /*
     *  Address: 0xe109ecb193841af9da3110c80fdd365d1c23be2a
     */

    // The starting value (0.01 USD at 1eth:$2 exchange rate)
    uint constant INITIAL_DEFAUlT_PAYMENT = 5 finney;

    uint public defaultPayment;

    function Scheduler() {
        defaultPayment = INITIAL_DEFAUlT_PAYMENT;
    }

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

    // Default payment and donation values
    modifier only_known_call { if (isKnownCall(msg.sender)) _ }

    function updateDefaultPayment() public only_known_call {
        var call = FutureBlockCall(msg.sender);
        var basePayment = call.basePayment();

        if (call.wasCalled() && call.claimer() != 0x0 && basePayment > 0 && defaultPayment > 1) {
            var index = call.claimAmount() * 100 / basePayment;

            if (index > 66) {
                // increase by 0.01%
                defaultPayment = defaultPayment * 10001 / 10000;
            }
            else if (index < 33) {
                // decrease by 0.01%
                defaultPayment = defaultPayment * 9999 / 10000;
            }
        }
    }

    function getDefaultDonation() constant returns (uint) {
        return defaultPayment / 100;
    }

    function getMinimumCallGas() constant returns (uint) {
        return SchedulerLib.getMinimumCallGas();
    }

    function getMaximumCallGas() constant returns (uint) {
        return SchedulerLib.getMaximumCallGas();
    }

    function getMinimumEndowment() constant returns (uint) {
        return SchedulerLib.getMinimumEndowment(defaultPayment, getDefaultDonation(), 0, getDefaultRequiredGas());
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
        return SchedulerLib.getFirstSchedulableBlock();
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

    function getDefaultStackCheck() constant returns (uint16) {
        return getMinimumStackCheck();
    }

    function getDefaultRequiredGas() constant returns (uint) {
        return SchedulerLib.getMinimumCallGas();
    }

    function getDefaultGracePeriod() constant returns (uint8) {
        return SchedulerLib.getDefaultGracePeriod();
    }

    // Ten minutes into the future (duplicated from SchedulerLib)
    bytes constant EMPTY_CALL_DATA = "";
    uint constant DEFAULT_CALL_VALUE = 0;
    bytes4 constant DEFAULT_FN_SIGNATURE = 0x0000;

    function scheduleCall() public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            DEFAULT_FN_SIGNATURE, EMPTY_CALL_DATA, getDefaultGracePeriod(), getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, getFirstSchedulableBlock(), getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(uint targetBlock) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            DEFAULT_FN_SIGNATURE, EMPTY_CALL_DATA, getDefaultGracePeriod(), getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, targetBlock, getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes callData) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            DEFAULT_FN_SIGNATURE, callData, getDefaultGracePeriod(), getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, getFirstSchedulableBlock(), getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes4 abiSignature,
                          bytes callData) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            abiSignature, callData, getDefaultGracePeriod(), getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, getFirstSchedulableBlock(), getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes4 abiSignature) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            abiSignature, EMPTY_CALL_DATA, getDefaultGracePeriod(), getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, getFirstSchedulableBlock(), getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            DEFAULT_FN_SIGNATURE, EMPTY_CALL_DATA, getDefaultGracePeriod(), getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, getFirstSchedulableBlock(), getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, EMPTY_CALL_DATA, getDefaultGracePeriod(), getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, getFirstSchedulableBlock(), getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          uint callValue,
                          bytes4 abiSignature) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, EMPTY_CALL_DATA, getDefaultGracePeriod(), getDefaultStackCheck(),
            callValue, getFirstSchedulableBlock(), getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          bytes callData) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, callData, getDefaultGracePeriod(), getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, getFirstSchedulableBlock(), getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          uint callValue,
                          bytes callData) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, callData, getDefaultGracePeriod(), getDefaultStackCheck(),
            callValue, getFirstSchedulableBlock(), getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(uint callValue,
                          address contractAddress) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            DEFAULT_FN_SIGNATURE, EMPTY_CALL_DATA, getDefaultGracePeriod(), getDefaultStackCheck(),
            callValue, getFirstSchedulableBlock(), getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          uint targetBlock) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            DEFAULT_FN_SIGNATURE, EMPTY_CALL_DATA, getDefaultGracePeriod(), getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, targetBlock, getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          uint targetBlock,
                          uint callValue) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            DEFAULT_FN_SIGNATURE, EMPTY_CALL_DATA, getDefaultGracePeriod(), getDefaultStackCheck(),
            callValue, targetBlock, getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes4 abiSignature,
                          uint targetBlock) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            abiSignature, EMPTY_CALL_DATA, getDefaultGracePeriod(), getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, targetBlock, getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          uint targetBlock) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, EMPTY_CALL_DATA, getDefaultGracePeriod(), getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, targetBlock, getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes4 abiSignature,
                          bytes callData,
                          uint targetBlock) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            abiSignature, callData, getDefaultGracePeriod(), getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, targetBlock, getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          bytes callData,
                          uint targetBlock) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, callData, getDefaultGracePeriod(), getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, targetBlock, getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
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
            abiSignature, callData, getDefaultGracePeriod(), getDefaultStackCheck(),
            callValue, targetBlock, getDefaultRequiredGas(), defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes4 abiSignature,
                          uint targetBlock,
                          uint requiredGas) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            abiSignature, EMPTY_CALL_DATA, getDefaultGracePeriod(), getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          uint targetBlock,
                          uint requiredGas) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, contractAddress,
            abiSignature, EMPTY_CALL_DATA, getDefaultGracePeriod(), getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes4 abiSignature,
                          bytes callData,
                          uint targetBlock,
                          uint requiredGas) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            abiSignature, callData, getDefaultGracePeriod(), getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, defaultPayment, getDefaultDonation(), msg.value
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
            abiSignature, callData, getDefaultGracePeriod(), getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, defaultPayment, getDefaultDonation(), msg.value
        );
    }

    function scheduleCall(bytes4 abiSignature,
                          uint targetBlock,
                          uint requiredGas,
                          uint8 gracePeriod) public returns (address) {
        return SchedulerLib.scheduleCall(
            callIndex,
            msg.sender, msg.sender,
            abiSignature, EMPTY_CALL_DATA, gracePeriod, getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, defaultPayment, getDefaultDonation(), msg.value
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
            abiSignature, EMPTY_CALL_DATA, gracePeriod, getDefaultStackCheck(),
            callValue, targetBlock, requiredGas, defaultPayment, getDefaultDonation(), msg.value
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
            abiSignature, EMPTY_CALL_DATA, gracePeriod, getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, defaultPayment, getDefaultDonation(), msg.value
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
            abiSignature, callData, gracePeriod, getDefaultStackCheck(),
            DEFAULT_CALL_VALUE, targetBlock, requiredGas, defaultPayment, getDefaultDonation(), msg.value
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
            abiSignature, EMPTY_CALL_DATA, gracePeriod, getDefaultStackCheck(),
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
            abiSignature, EMPTY_CALL_DATA, gracePeriod, getDefaultStackCheck(),
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
            abiSignature, EMPTY_CALL_DATA, gracePeriod, getDefaultStackCheck(),
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
            abiSignature, callData, gracePeriod, getDefaultStackCheck(),
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
            abiSignature, callData, gracePeriod, getDefaultStackCheck(),
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
            abiSignature, callData, gracePeriod, getDefaultStackCheck(),
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
