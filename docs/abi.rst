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
interact with the Alarm and CallerPool service.


Abstract Alarm Contract Source Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: solidity

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

            function getCallerPoolAddress() public returns (address);
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


Abstract CallerPool Contract Source Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: solidity

    contract CallerPoolAPI {
            /*
             *  Bond managment API.
             */
            function callerBonds(address callerAddress) public returns (uint);
            function getMinimumBond() public returns (uint);
            function depositBond() public;
            function withdrawBond(uint value) public;
            
            /*
             *  CallerPool <=> Alarm api.
             */
            function getDesignatedCaller(bytes32 callKey, uint targetBlock, uint8 gracePeriod, uint blockNumber) public returns (address);

            event AwardedMissedBlockBonus(address indexed fromCaller, address indexed toCaller, uint indexed poolNumber, bytes32 callKey, uint blockNumber, uint bonusAmount);

            /*
             *  Pool querying
             */
            function poolHistory(uint index) returns (uint);
            function getPoolKeyForBlock(uint blockNumber) public returns (uint);
            function getActivePoolKey() public returns (uint);
            function getNextPoolKey() public returns (uint);
            function getPoolSize(uint poolKey) returns (uint);

            /*
             *  Pool membership API
             */
            function isInAnyPool(address callerAddress) public returns (bool);
            function isInPool(address callerAddress, uint poolNumber) public returns (bool);

            /*
             *  Enter/Exit pool API
             */
            function canEnterPool(address callerAddress) public returns (bool);
            function canExitPool(address callerAddress) public returns (bool);
            function enterPool() public;
            function exitPool() public;
    }


Only use what you need
^^^^^^^^^^^^^^^^^^^^^^

The contracts above have stub functions for every API exposed by Alarm and
CallerPool.  It is safe to remove any functions or events from the abstract
contracts that you do not intend to use.
