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


Abstract Scheduler Contract Source Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following abstract solidity contract can be used to interact with the
scheduling contract from a solidity contract.


.. code-block:: solidity

    contract SchedulerAPI {
        /*
         *  Call Scheduling API
         */
        function getMinimumGracePeriod() constant returns (uint);
        function getDefaultPayment() constant returns (uint);
        function getDefaultFee() constant returns (uint);

        function isKnownCall(address callAddress) constant returns (bool);

        function scheduleCall(address contractAddress, bytes4 abiSignature, uint targetBlock) public returns (address);
        function scheduleCall(address contractAddress, bytes4 abiSignature, uint targetBlock, uint suggestedGas) public returns (address);
        function scheduleCall(address contractAddress, bytes4 abiSignature, uint targetBlock, uint suggestedGas, uint8 gracePeriod) public returns (address);
        function scheduleCall(address contractAddress, bytes4 abiSignature, uint targetBlock, uint suggestedGas, uint8 gracePeriod, uint basePayment) public returns (address);
        function scheduleCall(address contractAddress, bytes4 abiSignature, uint targetBlock, uint suggestedGas, uint8 gracePeriod, uint basePayment, uint baseFee) public returns (address);

        /*
         *  Call Execution API
         */
        function execute(address callAddress) public;

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
        function getGenerationIdForCall(address callAddress) constant returns (uint);
        function getDesignatedCaller(address callAddress, uint blockNumber) constant returns (bool, address);
        function getNextCall(uint blockNumber) constant returns (bytes32);
        function getNextCallSibling(address callAddress) constant returns (bytes32);
    }


Abstract Call Contract Source Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following abstract solidity contract can be used to interact with a call
contract from a solidity contract.

.. code-block:: solidity

    contract CallContractAPI {
        uint public targetBlock;
        uint8 public gracePeriod;

        address public owner;
        address public schedulerAddress;

        uint public basePayment;
        uint public baseFee;

        function contractAddress() constant returns (address);
        function abiSignature() constant returns (bytes4);
        function callData() constant returns (bytes);
        function anchorGasPrice() constant returns (uint);
        function suggestedGas() constant returns (uint);

        function isAlive() constant public;

        // cancel and registerData are only callable by the scheduler of the
        call contract.
        function cancel() public onlyscheduler;
        function registerData() public onlyscheduler;
    }


Only use what you need
^^^^^^^^^^^^^^^^^^^^^^

The contracts above have stub functions for every API exposed by Alarm and
CallerPool.  It is safe to remove any functions or events from the abstract
contracts that you do not intend to use.
