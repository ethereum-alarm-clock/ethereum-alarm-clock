contract AlarmAPI {
        /*
         *  Account Management API
         */
        function getAccountBalance(address accountAddress) constant public returns (uint);
        function deposit() public;
        function deposit(address accountAddress) public;
        function withdraw(uint value) public;

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
        function getLastCallKey() constant returns (bytes32);
        function getLastDataHash() constant returns (bytes32);
        function getLastDataLength() constant returns (uint);
        function getLastData() constant returns (bytes);

        function getCallData(bytes32 callKey) constant returns (bytes);
        function getCallContractAddress(bytes32 callKey) constant returns (address);
        function getCallScheduledBy(bytes32 callKey) constant returns (address);
        function getCallCalledAtBlock(bytes32 callKey) constant returns (uint);
        function getCallGracePeriod(bytes32 callKey) constant returns (uint);
        function getCallTargetBlock(bytes32 callKey) constant returns (uint);
        function getCallBaseGasPrice(bytes32 callKey) constant returns (uint);
        function getCallGasPrice(bytes32 callKey) constant returns (uint);
        function getCallGasUsed(bytes32 callKey) constant returns (uint);
        function getCallABISignature(bytes32 callKey) constant returns (bytes4);
        function checkIfCalled(bytes32 callKey) constant returns (bool);
        function checkIfSuccess(bytes32 callKey) constant returns (bool);
        function checkIfCancelled(bytes32 callKey) constant returns (bool);
        function getCallDataHash(bytes32 callKey) constant returns (bytes32);
        function getCallPayout(bytes32 callKey) constant returns (uint);
        function getCallFee(bytes32 callKey) constant returns (uint);
        function getCallMaxCost(bytes32 callKey) constant returns (uint);

        /*
         *  Call Scheduling API
         */
        function getMinimumGracePeriod() constant returns (uint);
        function scheduleCall(address contractAddress, bytes4 abiSignature, bytes32 dataHash, uint targetBlock) public;
        function scheduleCall(address contractAddress, bytes4 abiSignature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod) public;
        function scheduleCall(address contractAddress, bytes4 abiSignature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod, uint nonce) public;
        function cancelCall(bytes32 callKey) public;

        /*
         *  Call Execution API
         */
        function doCall(bytes32 callKey) public;

        /*
         *  Caller Pool bonding
         */
        function getMinimumBond() constant returns (uint);
        function depositBond() public;
        function withdrawBond(uint value) public;
        function getBondBalance() constant returns (uint);
        function getBondBalance(address callerAddress) constant returns (uint);

        /*
         *  Caller Pool Membership
         */
        function getGenerationForCall(bytes32 callKey) constant returns (uint);
        function getGenerationSize(uint generationId) constant returns (uint);
        function getGenerationStartAt(uint generationId) constant returns (uint);
        function getGenerationEndAt(uint generationId) constant returns (uint);
        function getCurrentGenerationId() constant returns (uint);
        function getNextGenerationId() constant returns (uint);
        function isInPool() constant returns (bool);
        function isInPool(address callerAddress) constant returns (bool);
        function isInGeneration(uint generationId) constant returns (bool);
        function isInGeneration(address callerAddress, uint generationId) constant returns (bool);

        /*
         *  Caller Pool Metadata
         */
        function getPoolFreezePeriod() constant returns (uint);
        function getPoolOverlapSize() constant returns (uint);
        function getPoolRotationDelay() constant returns (uint);

        /*
         *  Caller Pool Entering and Exiting
         */
        function canEnterPool() constant returns (bool);
        function canEnterPool(address callerAddress) constant returns (bool);
        function canExitPool() constant returns (bool);
        function canExitPool(address callerAddress) constant returns (bool);
        function enterPool() public;
        function exitPool() public;

        /*
         *  Next Call API
         */
        function getCallWindowSize() constant returns (uint);
        function getGenerationIdForCall(bytes32 callKey) constant returns (uint);
        function getDesignatedCaller(bytes32 callKey, uint blockNumber) constant returns (address);
        function getNextCall(uint blockNumber) constant returns (bytes32);
        function getNextCallSibling(bytes32 callKey) constant returns (bytes32);
}
