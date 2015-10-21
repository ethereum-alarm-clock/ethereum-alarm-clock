Contract ABI
============

Beyond the simplest use cases, the use of ``address.call`` to interact with the
Alarm service is limiting.  Beyond the readability issues, it is not possible
to get the return values from function calls when using ``call()``.

By using an abstract solidity contract which defines all of the function
signatures, you can easily call any of the Alarm service's functions, letting
the compiler handle computation of the function ABI signatures.


Abstract Solidity Contracts
---------------------------

The following abstract contracts can be used alongside your contract code to
interact with the Alarm service.


Abstract Alarm Contract Source Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: solidity
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


Register Data is special
^^^^^^^^^^^^^^^^^^^^^^^^

You may notice that the contract above is missing the ``registerData``
function.  This is because it is allowed to be called with any call signature
and solidity has no way of defining such a function.

Registering your data requires use of the ``address.call()`` api.

.. code-block::

    class Example {
        function scheduleIt() {
            address alarm = 0x...;
            alarm.call(bytes4(sha3("registerData()")), 3, 4, 'test');
        }
        ...
    }

Only use what you need
^^^^^^^^^^^^^^^^^^^^^^

The contracts above have stub functions for every API exposed by Alarm and
CallerPool.  It is safe to remove any functions or events from the abstract
contracts that you do not intend to use.
