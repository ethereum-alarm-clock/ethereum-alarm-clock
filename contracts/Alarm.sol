import "owned";


contract Alarm {
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
                        accountBalances[msg.sender] -= value;
                        msg.sender.send(value);
                }
        }

        function() {
                accountBalances[msg.sender] += msg.value;
        }

        /*
         *  Call tracking API
         */
        struct Node {
                bytes32 callKey;
                bytes32 left;
                bytes32 right;
                bytes position;
        }

        bytes32 public rootNodeCallKey;
        bytes32 public mostRecentCallKey;

        mapping (bytes32 => Node) call_to_node;

        function _shouldGoLeft(bytes32 callKey, uint blockNumber) internal returns (bool) {
                Node currentNode = call_to_node[callKey];

                // Nowhere to go.
                if (currentNode.left == 0x0) {
                        return false;
                }

                // Already called.
                if (callKey == mostRecentCallKey) {
                        return false;
                }

                Call currentCall = key_to_calls[callKey];

                // Current call is already in the past or is up next.
                if (currentCall.targetBlock <= blockNumber) {
                        return false;
                }

                Call leftCall = key_to_calls[currentNode.left];

                // Left call is in the past
                if (leftCall.targetBlock < blockNumber) {
                        return false;
                }

                return true;
        }

        function _shouldGoRight(bytes32 callKey, uint blockNumber) internal returns (bool) {
                Node currentNode = call_to_node[callKey];

                // Nowhere to go.
                if (currentNode.right == 0x0) {
                        return false;
                }

                Call currentCall = key_to_calls[callKey];

                // Current call is already in the future
                if (currentCall.targetBlock > blockNumber) {
                        return false;
                }

                if (callKey != mostRecentCallKey && currentCall.targetBlock == blockNumber) {
                        return false;
                }

                return true;
        }

        function getNextCallKey(uint blockNumber) public returns (bytes32) {
                if (rootNodeCallKey == 0x0) {
                        // No calls registered
                        return bytes32(0x0);
                }

                Node currentNode = call_to_node[rootNodeCallKey];
                
                bool hasLeft;
                bool hasRight;
                bool isEqual;
                bool isBefore;
                bool isAfter;
                bool isMostRecent;

                while (true) {
                        if (_shouldGoLeft(currentNode.callKey, blockNumber)) {
                                currentNode = call_to_node[currentNode.left];
                                continue;
                        }
                        if (_shouldGoRight(currentNode.callKey, blockNumber)) {
                                currentNode = call_to_node[currentNode.right];
                                continue;
                        }
                        if (currentNode.callKey == mostRecentCallKey) {
                                return bytes32(0x0);
                        }
                        return currentNode.callKey;
                }
        }

        function getCallTreePosition(bytes32 callKey) public returns (bytes) {
                return call_to_node[callKey].position;
        }

        function placeCallInTree(bytes32 callKey) internal {
                /*
                 * Calls are stored in a tree structure.  Each tree node
                 * represents a single call.  Nodes have a left and right
                 * child.  The left child represents a call that should happen
                 * before the node.  The right child represents a call that
                 * should happen after the node.
                 */
                Call targetCall = key_to_calls[callKey];

                if (callKey == call_to_node[callKey].callKey) {
                        // This call key is already placed in the tree.
                        return;
                }

                if (rootNodeCallKey == 0x0) {
                        // This is the first call placement and thus should be
                        // set as the root node.
                        rootNodeCallKey = callKey;
                }

                Node currentNode = call_to_node[rootNodeCallKey];

                bytes position;
                position.length = 1;
                position[0] = "b";

                while (true) {
                        if (currentNode.callKey == 0x0) {
                                // This is a new node and should be mapped 
                                currentNode.callKey = callKey;
                                currentNode.position = position;
                                return;
                        }

                        Call currentCall = key_to_calls[currentNode.callKey];
                        position.length += 1;

                        if (targetCall.targetBlock < currentCall.targetBlock) {
                                // Call should occure before the current node
                                // and thus should exist in the left subtree.
                                if (currentNode.left == 0x0) {
                                        currentNode.left = callKey;
                                }
                                position[position.length - 1] = "l";
                                currentNode = call_to_node[currentNode.left];
                                continue;
                        }

                        // Call should occur after the current node and thus
                        // should exist in the right subtree.
                        if (currentNode.right == 0x0) {
                                currentNode.right = callKey;
                        }
                        position[position.length - 1] = "r";
                        currentNode = call_to_node[currentNode.right];
                }
        }

        /*
         *  Call Information API
         */
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

        function getDataHash(bytes32 callKey) public returns (bytes32) {
                return key_to_calls[callKey].dataHash;
        }

        /*
         *  Data Registry API
         */
        bytes lastData;
        uint lastDataLength;
        bytes32 lastDataHash;

        function getLastDataHash() public returns (bytes32) {
                return lastDataHash;
        }

        function getLastDataLength() public returns (uint) {
                return lastDataLength;
        }

        function getLastData() public returns (bytes) {
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

                placeCallInTree(lastCallKey);

                return lastCallKey;
        }

        function __throw() internal {
                // workaround until we have "throw"
                uint[] x;
                x[1];
        }
}
