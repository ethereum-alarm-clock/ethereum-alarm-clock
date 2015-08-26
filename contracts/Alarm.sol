contract Alarm {
        bytes32 lastCallHash;
        bytes lastData;
        bytes32 lastDataHash;

        function getLastCallHash() public returns (bytes32) {
                return lastCallHash;
        }

        function getLastDataHash() public returns (bytes32) {
                return lastDataHash;
        }

        function getLastData() public returns (bytes) {
                return lastData;
        }

        // Fallback function so that contract can receive direct deposits.
        function() {
        }

        struct Call {
                address to;
                uint calledAtBlock;
                uint targetBlock;
                uint deposit;
                uint gasBefore;
                uint gasAfter;
                uint gasPrice;
                address triggeredBy;
                bytes4 sig;
                bool wasCalled;
                bytes data;
        }

        mapping (bytes32 => Call) hash_to_calls;
        mapping (uint => Call[]) block_to_calls;
        mapping (bytes32 => bytes) hash_to_data;

        function getCallValue(bytes32 callHash) public returns (uint) {
                return hash_to_calls[callHash].deposit;
        }

        function getGasBefore(bytes32 callHash) public returns (uint) {
                return hash_to_calls[callHash].gasBefore;
        }

        function getGasAfter(bytes32 callHash) public returns (uint) {
                return hash_to_calls[callHash].gasAfter;
        }

        function doCall(bytes32 callHash) public returns (bool) {
                var call = hash_to_calls[callHash];
                call.gasBefore = msg.gas;
                call.gasPrice = tx.gasprice;
                call.triggeredBy = tx.origin;
                call.calledAtBlock = block.number;
                bool callSucceeded = call.to.call(call.sig, call.data);
                call.gasAfter = msg.gas;
                return callSucceeded;
        }

        //event DataRegistered(bytes32 dataHash, bytes data);

        function registerData() public {
                bytes trunc;
                trunc.length = msg.data.length - 4;
                for (uint i = 0; i < trunc.length - 1; i++) {
                        trunc[trunc.length - 1 - i] = msg.data[msg.data.length - 1 - i];
                }
                hash_to_data[sha3(trunc)] = trunc;
                lastDataHash = sha3(trunc);
                lastData = msg.data;
        }

        function getCallHash(bytes4 signature, bytes32 dataHash, uint targetBlock) public returns (bytes32) {
                var data = hash_to_data[dataHash];
                return sha3(msg.sender, signature, data, targetBlock);
        }

        //event CallScheduled(address to, bytes4 signature, bytes32 dataHash, uint targetBlock);

        function scheduleCall(bytes4 signature, bytes32 dataHash, uint targetBlock) public returns (bytes32) {
                var data = hash_to_data[dataHash];
                lastCallHash = getCallHash(signature, dataHash, targetBlock);

                var call = hash_to_calls[lastCallHash];
                call.to = msg.sender;
                call.sig = signature;
                call.data = data;
                call.targetBlock = targetBlock;
                call.deposit = msg.value;

                return lastCallHash;
        }
}
