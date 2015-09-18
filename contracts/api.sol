contract AlarmAPI {
        /*
         *  Account Management API
         */
        function accountBalances(address account) public returns (uint);

        event Deposit(address indexed _from, address indexed accountAddress, uint value);
        function deposit(address accountAddress) public;

        event Withdraw(address indexed accountAddress, uint value);
        function withdraw(uint value) public;

        /*
         *  Call Tree API
         */
        event CallPlacedInTree(bytes32 indexed callKey);
        event TreeRotatedLeft(bytes32 indexed oldRootNodeCallKey, bytes32 indexed newRootNodeCallKey);
        event TreeRotatedRight(bytes32 indexed oldRootNodeCallKey, bytes32 indexed newRootNodeCallKey);

        function rootNodeCallKey() returns (bytes32);
        function getNextBlockWithCall(uint blockNumber) returns (uint);
        function getNextCallKey(uint blockNumber) returns (bytes32);
        function getNextCallSibling(bytes32 callKey) public returns (bytes32);
        function getCallLeftChild(bytes32 callKey) public returns (bytes32);
        function getCallRightChild(bytes32 callKey) public returns (bytes32);
        function rotateTree() public;

        /*
         *  Authorization API
         */
        function unauthorizedAddress() public returns (address);
        function authorizedAddress() public returns (address);
        function addAuthorization(address schedulerAddress) public;
        function removeAuthorization(address schedulerAddress) public;
        function checkAuthorization(address schedulerAddress, address contractAddress) public returns (bool);

        /*
         *  Scheduled Call Meta API
         */
        function getLastCallKey() public returns (bytes32);
        function getLastDataHash() public returns (bytes32);
        function getLastDataLength() public returns (uint);
        function getLastData() public returns (bytes);

        function getCallContractAddress(bytes32 callKey) public returns (address);
        function getCallScheduledBy(bytes32 callKey) public returns (address);
        function getCallCalledAtBlock(bytes32 callKey) public returns (uint);
        function getCallGracePeriod(bytes32 callKey) public returns (uint);
        function getCallTargetBlock(bytes32 callKey) public returns (uint);
        function getCallBaseGasPrice(bytes32 callKey) public returns (uint);
        function getCallGasPrice(bytes32 callKey) public returns (uint);
        function getCallGasUsed(bytes32 callKey) public returns (uint);
        function getCallABISignature(bytes32 callKey) public returns (bytes4);
        function checkIfCalled(bytes32 callKey) public returns (bool);
        function checkIfSuccess(bytes32 callKey) public returns (bool);
        function checkIfCancelled(bytes32 callKey) public returns (bool);
        function getCallDataHash(bytes32 callKey) public returns (bytes32);
        function getCallPayout(bytes32 callKey) public returns (uint);
        function getCallFee(bytes32 callKey) public returns (uint);
        function getCallData(bytes32 callKey) public returns (bytes);

        /*
         *  Call Data Registration API
         */
        event DataRegistered(bytes32 indexed dataHash);
        function registerData() public;

        /*
         *  Call Scheduling API
         */
        event CallScheduled(bytes32 indexed callKey);
        event CallRejected(bytes32 indexed callKey, bytes12 reason);
        event CallCancelled(bytes32 indexed callKey);

        function getCallKey(address scheduledBy, address contractAddress, bytes4 abiSignature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod, uint nonce) public returns (bytes32);
        function scheduleCall(address contractAddress, bytes4 abiSignature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod, uint nonce) public;
        function cancelCall(bytes32 callKey) public;

        /*
         *  Call Execution API
         */
        event CallExecuted(address indexed executedBy, bytes32 indexed callKey);
        event CallAborted(address indexed executedBy, bytes32 indexed callKey, bytes18 reason);

        function doCall(bytes32 callKey) public;
        function getCallMaxCost(bytes32 callKey) public returns (uint);
        function getCallFeeScalar(uint baseGasPrice, uint gasPrice) public returns (uint);

}
