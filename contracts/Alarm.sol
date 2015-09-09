import "owned";


contract DataRegistryAPI {
        function getCallData(bytes32 dataHash) public returns (bytes) {}
}


contract Alarm is owned {
        address dataRegistryAddress;

        bytes32 lastCallKey;

        function getLastCallKey() public returns (bytes32) {
                return lastCallKey;
        }

        struct Call {
                address targetAddress;
                address scheduledBy;
                uint calledAtBlock;
                uint targetBlock;
                uint deposit;
                uint gasPrice;
                uint gasUsed;
                address triggeredBy;
                bytes4 sig;
                bool wasCalled;
                bool wasSuccessful;
                bytes32 dataHash;
        }

        mapping (bytes32 => Call) key_to_calls;

        /*
         *  Getter methods for `Call` information
         */
        function getCallTargetAddress(bytes32 callKey) public returns (address) {
                return key_to_calls[callKey].targetAddress;
        }

        function getCallScheduledBy(bytes32 callKey) public returns (address) {
                return key_to_calls[callKey].scheduledBy;
        }

        function getCallCalledAtBlock(bytes32 callKey) public returns (uint) {
                return key_to_calls[callKey].calledAtBlock;
        }

        function getCallTargetBlock(bytes32 callKey) public returns (uint) {
                return key_to_calls[callKey].targetBlock;
        }

        function getCallDeposit(bytes32 callKey) public returns (uint) {
                return key_to_calls[callKey].deposit;
        }

        function getCallGasPrice(bytes32 callKey) public returns (uint) {
                return key_to_calls[callKey].gasPrice;
        }

        function getCallGasUsed(bytes32 callKey) public returns (uint) {
                return key_to_calls[callKey].gasUsed;
        }

        function getCallSignature(bytes32 callKey) public returns (bytes4) {
                return key_to_calls[callKey].sig;
        }

        function checkIfCalled(bytes32 callKey) public returns (bool) {
                return key_to_calls[callKey].wasCalled;
        }

        function checkIfSuccess(bytes32 callKey) public returns (bool) {
                return key_to_calls[callKey].wasSuccessful;
        }

        function getCallData(bytes32 callKey) public returns (bytes) {
                DataRegistryAPI dataRegistry = DataRegistryAPI(dataRegistryAddress);
                return dataRegistry.getCallData(key_to_calls[callKey].dataHash);
        }

        /*
         *  Main Alarm API
         */
        function doCall(bytes32 callKey) public returns (bool) {
                uint gasBefore = msg.gas;

                var call = key_to_calls[callKey];
                call.gasPrice = tx.gasprice;
                call.triggeredBy = tx.origin;
                call.calledAtBlock = block.number;

                call.wasSuccessful = call.targetAddress.call(call.sig, call.data);
                call.wasCalled = true;

                // Log how much gas this call used.
                call.gasUsed = gasBefore - msg.gas;

                return call.wasSuccessful;
        }

        // The result of `sha()` so that we can validate that people aren't
        // looking up call data that failed to register.
        bytes32 constant emptyDataHash = 0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470;

        function getCallKey(address to, bytes4 signature, bytes32 dataHash, uint targetBlock) public returns (bytes32) {
                return sha3(to, signature, dataHash, targetBlock);
        }

        event CallScheduled(address to, bytes4 signature, bytes32 dataHash, uint targetBlock);

        function scheduleCall(address to, bytes4 signature, bytes32 dataHash, uint targetBlock) public returns (bytes32) {
                lastCallKey = getCallKey(to, signature, dataHash, targetBlock);

                var call = key_to_calls[lastCallKey];
                call.targetAddress = to;
                call.scheduledBy = msg.sender;
                call.sig = signature;
                call.dataHash = dataHash;
                call.targetBlock = targetBlock;
                call.deposit = msg.value;

                return lastCallKey;
        }

        function __throw() internal {
                // workaround until we have "throw"
                uint[] x;
                x[1];
        }
}
