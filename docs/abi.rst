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
        function getDefaultDonation() constant returns (uint);
        function getMinimumCallGas() constant returns (uint);
        function getMaximumCallGas() constant returns (uint);
        function getMinimumEndowment() constant returns (uint);
        function getMinimumEndowment(uint basePayment) constant returns (uint);
        function getMinimumEndowment(uint basePayment, uint baseDonation) constant returns (uint);
        function getMinimumEndowment(uint basePayment, uint baseDonation, uint callValue) constant returns (uint);
        function getMinimumEndowment(uint basePayment, uint baseDonation, uint callValue, uint requiredGas) constant returns (uint);
        function isKnownCall(address callAddress) constant returns (bool);
        function getFirstSchedulableBlock() constant returns (uint);
        function getMinimumStackCheck() constant returns (uint16);
        function getMaximumStackCheck() constant returns (uint16);
        function getDefaultStackCheck() constant returns (uint16);
        function getDefaultRequiredGas() constant returns (uint);
        function getDefaultGracePeriod() constant returns (uint8);


        /*
         *  Next Call API
         */
        function getCallWindowSize() constant returns (uint);
        function getNextCall(uint blockNumber) constant returns (bytes32);
        function getNextCallSibling(address callAddress) constant returns (bytes32);
    }


Abstract Call Contract Source Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following abstract solidity contract can be used to interact with a call
contract from a solidity contract.

.. code-block:: solidity

    contract CallContractAPI {
        bytes public callData;
        address public contractAddress;
        uint8 public gracePeriod;
        address public schedulerAddress;
        uint public requiredGas;
        bool public isCancelled;
        bool public wasCalled;
        bool public wasSuccessful;
        uint public anchorGasPrice;
        uint public basePayment;
        bytes4 public abiSignature;
        uint public baseFee;
        uint public targetBlock;
        uint16 public requiredStackDepth;

        function execute() public;
        function cancel() public;

        function claim() public;

        address public claimer;
        uint public claimerDeposit;
        uint public claimAmount;

        function checkExecutionAuthorization(address executor, uint256 block_number) public returns (bool)

        function getClaimAmountForBlock() public returns (uint);
        function getClaimAmountForBlock(uint256 block_number) public returns (uint);

        function registerData() public;
    }


Only use what you need
^^^^^^^^^^^^^^^^^^^^^^

The contracts above have stub functions for every API exposed by Alarm and
CallerPool.  It is safe to remove any functions or events from the abstract
contracts that you do not intend to use.
