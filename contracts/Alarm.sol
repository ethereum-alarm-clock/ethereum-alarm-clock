import "owned";


contract Alarm is owned {
        /*
         *  Account Management API
         */
        mapping (address => uint) public accountBalances;

        function deposit(address accountAddress) {
                accountBalances[accountAddress] += msg.value;
        }

        function withdraw(uint value) {
                uint accountBalance = accountBalances[msg.sender];
                if (accountBalance >= value) {
                        msg.sender.send(value);
                }
        }

        function() {
                accountBalances[msg.sender] += msg.value;
        }

        /*
         *  Call Information API
         */
        bytes32 lastCallKey;

        function getLastCallKey() onlyowner public returns (bytes32) {
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

        function getDataHash(bytes32 callKey) public returns (bytes32) {
                return key_to_calls[callKey].dataHash;
        }

        /*
         *  Data Registry API
         */
        bytes lastData;
        uint lastDataLength;
        bytes32 lastDataHash;

        function getLastDataHash() onlyowner public returns (bytes32) {
                return lastDataHash;
        }

        function getLastDataLength() onlyowner public returns (uint) {
                return lastDataLength;
        }

        function getLastData() onlyowner public returns (bytes) {
                return lastData;
        }

        function getCallData(bytes32 callKey) public returns (bytes) {
                return hash_to_data[key_to_calls[callKey].dataHash];
        }

        mapping (bytes32 => bytes) hash_to_data;

        /*
         *  Main Alarm API
         */
        event DataRegistered(address registeredBy, bytes32 dataHash, bytes data);

        function registerData() public {
                bytes trunc;
                if (msg.data.length > 4) {
                        trunc.length = msg.data.length - 4;
                        for (uint i = 0; i < trunc.length; i++) {
                                trunc[trunc.length - 1 - i] = msg.data[msg.data.length - 1 - i];
                        }
                }
                hash_to_data[sha3(trunc)] = trunc;
                lastDataHash = sha3(trunc);
                lastDataLength = trunc.length;
                lastData = trunc;
                DataRegistered(msg.sender, lastDataHash, lastData);
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

                var data = getCallData(callKey);

                call.wasSuccessful = call.targetAddress.call(call.sig, data);
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
