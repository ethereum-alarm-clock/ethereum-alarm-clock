contract Alarm {
        //function Alarm() {
        //        owner = tx.origin;
        //}

        //address owner;

        //modifier onlyowner { if (msg.sender == owner) _ }

        bytes32 lastCallKey;
        bytes lastData;
        uint lastDataLength;
        bytes32 lastDataHash;

        function getLastCallKey() public returns (bytes32) {
                return lastCallKey;
        }

        function getLastDataHash() public returns (bytes32) {
                return lastDataHash;
        }

        function getLastDataLength() public returns (uint) {
                return lastDataLength;
        }

        function getLastData() public returns (bytes) {
                return lastData;
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
                bytes data;
        }

        mapping (bytes32 => Call) key_to_calls;
        mapping (bytes32 => bytes) hash_to_data;

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
                return key_to_calls[callKey].data;
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

        event DataRegistered(address registeredBy, bytes32 dataHash, bytes data);

        function registerData() public {
                bytes trunc;
                if (msg.data.length > 4) {
                        trunc.length = msg.data.length - 4;
                        for (uint i = 0; i < trunc.length; i++) {
                                trunc[trunc.length - 1 - i] = msg.data[msg.data.length - 1 - i];
                        }
                        hash_to_data[sha3(trunc)] = trunc;
                }
                lastDataHash = sha3(trunc);
                lastDataLength = trunc.length;
                lastData = trunc;
                DataRegistered(msg.sender, lastDataHash, lastData);
        }

        // The result of `sha()` so that we can validate that people aren't
        // looking up call data that failed to register.
        bytes32 constant emptyDataHash = 0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470;

        function getCallKey(address to, bytes4 signature, bytes32 dataHash, uint targetBlock) public returns (bytes32) {
                var data = hash_to_data[dataHash];
                if (data.length == 0 && dataHash != emptyDataHash) {
                        __throw();
                }
                return sha3(to, signature, data, targetBlock);
        }

        event CallScheduled(address to, bytes4 signature, bytes32 dataHash, uint targetBlock);

        function scheduleCall(address to, bytes4 signature, bytes32 dataHash, uint targetBlock) public returns (bytes32) {
                var data = hash_to_data[dataHash];
                lastCallKey = getCallKey(to, signature, dataHash, targetBlock);

                var call = key_to_calls[lastCallKey];
                call.targetAddress = to;
                call.scheduledBy = msg.sender;
                call.sig = signature;
                call.data = data;
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
