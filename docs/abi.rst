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


Contract ABI
------------

If you would like to interact with these contracts either from the javascript
console, or the Ethereum wallet, you can use the following contract ABI.


Scheduler ABI
^^^^^^^^^^^^^

.. code-block:: javascript

    [
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "callValue",
                    "type": "uint256"
                },
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                },
                {
                    "name": "requiredGas",
                    "type": "uint256"
                },
                {
                    "name": "gracePeriod",
                    "type": "uint8"
                },
                {
                    "name": "basePayment",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                },
                {
                    "name": "requiredGas",
                    "type": "uint256"
                },
                {
                    "name": "gracePeriod",
                    "type": "uint8"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "callData",
                    "type": "bytes"
                },
                {
                    "name": "requiredStackDepth",
                    "type": "uint16"
                },
                {
                    "name": "gracePeriod",
                    "type": "uint8"
                },
                {
                    "name": "args",
                    "type": "uint256[5]"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "callData",
                    "type": "bytes"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "targetBlock",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "getDefaultStackCheck",
            "outputs": [
                {
                    "name": "",
                    "type": "uint16"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "getMinimumEndowment",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "getMaximumCallGas",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "callAPIVersion",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "callValue",
                    "type": "uint256"
                },
                {
                    "name": "callData",
                    "type": "bytes"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                },
                {
                    "name": "requiredGas",
                    "type": "uint256"
                },
                {
                    "name": "gracePeriod",
                    "type": "uint8"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "callValue",
                    "type": "uint256"
                },
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "callData",
                    "type": "bytes"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                },
                {
                    "name": "requiredGas",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [
                {
                    "name": "callAddress",
                    "type": "address"
                }
            ],
            "name": "getNextCallSibling",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "callData",
                    "type": "bytes"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "callData",
                    "type": "bytes"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                },
                {
                    "name": "requiredGas",
                    "type": "uint256"
                },
                {
                    "name": "gracePeriod",
                    "type": "uint8"
                },
                {
                    "name": "basePayment",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [
                {
                    "name": "callAddress",
                    "type": "address"
                }
            ],
            "name": "isKnownCall",
            "outputs": [
                {
                    "name": "",
                    "type": "bool"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "getMaximumStackCheck",
            "outputs": [
                {
                    "name": "",
                    "type": "uint16"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "callData",
                    "type": "bytes"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                },
                {
                    "name": "requiredGas",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "callValue",
                    "type": "uint256"
                },
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                },
                {
                    "name": "requiredGas",
                    "type": "uint256"
                },
                {
                    "name": "gracePeriod",
                    "type": "uint8"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "callData",
                    "type": "bytes"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                },
                {
                    "name": "requiredGas",
                    "type": "uint256"
                },
                {
                    "name": "gracePeriod",
                    "type": "uint8"
                },
                {
                    "name": "basePayment",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "callValue",
                    "type": "uint256"
                },
                {
                    "name": "callData",
                    "type": "bytes"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "callData",
                    "type": "bytes"
                },
                {
                    "name": "gracePeriod",
                    "type": "uint8"
                },
                {
                    "name": "args",
                    "type": "uint256[4]"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [
                {
                    "name": "basePayment",
                    "type": "uint256"
                },
                {
                    "name": "baseDonation",
                    "type": "uint256"
                },
                {
                    "name": "callValue",
                    "type": "uint256"
                }
            ],
            "name": "getMinimumEndowment",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                },
                {
                    "name": "requiredGas",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "defaultPayment",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "getDefaultGracePeriod",
            "outputs": [
                {
                    "name": "",
                    "type": "uint8"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "callData",
                    "type": "bytes"
                },
                {
                    "name": "requiredStackDepth",
                    "type": "uint16"
                },
                {
                    "name": "gracePeriod",
                    "type": "uint8"
                },
                {
                    "name": "callValue",
                    "type": "uint256"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                },
                {
                    "name": "requiredGas",
                    "type": "uint256"
                },
                {
                    "name": "basePayment",
                    "type": "uint256"
                },
                {
                    "name": "baseDonation",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "getMinimumStackCheck",
            "outputs": [
                {
                    "name": "",
                    "type": "uint16"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "callData",
                    "type": "bytes"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                },
                {
                    "name": "requiredGas",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "getMinimumCallGas",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "getCallWindowSize",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [
                {
                    "name": "blockNumber",
                    "type": "uint256"
                }
            ],
            "name": "getNextCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "callValue",
                    "type": "uint256"
                },
                {
                    "name": "contractAddress",
                    "type": "address"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "callData",
                    "type": "bytes"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [
                {
                    "name": "basePayment",
                    "type": "uint256"
                }
            ],
            "name": "getMinimumEndowment",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "getFirstSchedulableBlock",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "callData",
                    "type": "bytes"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                },
                {
                    "name": "requiredGas",
                    "type": "uint256"
                },
                {
                    "name": "gracePeriod",
                    "type": "uint8"
                },
                {
                    "name": "basePayment",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "getDefaultDonation",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "getMinimumGracePeriod",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                },
                {
                    "name": "callValue",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "getDefaultRequiredGas",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                },
                {
                    "name": "requiredGas",
                    "type": "uint256"
                },
                {
                    "name": "gracePeriod",
                    "type": "uint8"
                },
                {
                    "name": "basePayment",
                    "type": "uint256"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [],
            "name": "updateDefaultPayment",
            "outputs": [],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [
                {
                    "name": "basePayment",
                    "type": "uint256"
                },
                {
                    "name": "baseDonation",
                    "type": "uint256"
                },
                {
                    "name": "callValue",
                    "type": "uint256"
                },
                {
                    "name": "requiredGas",
                    "type": "uint256"
                }
            ],
            "name": "getMinimumEndowment",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "contractAddress",
                    "type": "address"
                },
                {
                    "name": "abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "callData",
                    "type": "bytes"
                },
                {
                    "name": "targetBlock",
                    "type": "uint256"
                },
                {
                    "name": "requiredGas",
                    "type": "uint256"
                },
                {
                    "name": "gracePeriod",
                    "type": "uint8"
                }
            ],
            "name": "scheduleCall",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [
                {
                    "name": "basePayment",
                    "type": "uint256"
                },
                {
                    "name": "baseDonation",
                    "type": "uint256"
                }
            ],
            "name": "getMinimumEndowment",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "inputs": [],
            "type": "constructor"
        }
    ]


Call Contract ABI
^^^^^^^^^^^^^^^^^

.. code-block:: javascript

    [
        {
            "constant": true,
            "inputs": [],
            "name": "wasSuccessful",
            "outputs": [
                {
                    "name": "",
                    "type": "bool"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "targetBlock",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "firstClaimBlock",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "getExtraGas",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [
                {
                    "name": "n",
                    "type": "uint256"
                }
            ],
            "name": "__dig",
            "outputs": [
                {
                    "name": "",
                    "type": "bool"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [
                {
                    "name": "executor",
                    "type": "address"
                },
                {
                    "name": "block_number",
                    "type": "uint256"
                }
            ],
            "name": "checkExecutionAuthorization",
            "outputs": [
                {
                    "name": "",
                    "type": "bool"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "requiredStackDepth",
            "outputs": [
                {
                    "name": "",
                    "type": "uint16"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "callAPIVersion",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "claimerDeposit",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "anchorGasPrice",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "isCancellable",
            "outputs": [
                {
                    "name": "",
                    "type": "bool"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "callData",
            "outputs": [
                {
                    "name": "",
                    "type": "bytes"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [],
            "name": "claim",
            "outputs": [
                {
                    "name": "",
                    "type": "bool"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "getClaimAmountForBlock",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [],
            "name": "execute",
            "outputs": [],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "baseDonation",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "getOverhead",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {
                    "name": "executor",
                    "type": "address"
                },
                {
                    "name": "startGas",
                    "type": "uint256"
                }
            ],
            "name": "beforeExecute",
            "outputs": [
                {
                    "name": "",
                    "type": "bool"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "claimAmount",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "origin",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "isCancelled",
            "outputs": [
                {
                    "name": "",
                    "type": "bool"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "requiredGas",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "gracePeriod",
            "outputs": [
                {
                    "name": "",
                    "type": "uint8"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "lastClaimBlock",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "schedulerAddress",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [],
            "name": "registerData",
            "outputs": [
                {
                    "name": "",
                    "type": "bool"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "state",
            "outputs": [
                {
                    "name": "",
                    "type": "uint8"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "basePayment",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "wasCalled",
            "outputs": [
                {
                    "name": "",
                    "type": "bool"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "abiSignature",
            "outputs": [
                {
                    "name": "",
                    "type": "bytes4"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "maxClaimBlock",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "claimer",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "callValue",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [],
            "name": "cancel",
            "outputs": [],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [
                {
                    "name": "block_number",
                    "type": "uint256"
                }
            ],
            "name": "getClaimAmountForBlock",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "contractAddress",
            "outputs": [
                {
                    "name": "",
                    "type": "address"
                }
            ],
            "type": "function"
        },
        {
            "inputs": [
                {
                    "name": "_schedulerAddress",
                    "type": "address"
                },
                {
                    "name": "_targetBlock",
                    "type": "uint256"
                },
                {
                    "name": "_gracePeriod",
                    "type": "uint8"
                },
                {
                    "name": "_contractAddress",
                    "type": "address"
                },
                {
                    "name": "_abiSignature",
                    "type": "bytes4"
                },
                {
                    "name": "_callData",
                    "type": "bytes"
                },
                {
                    "name": "_callValue",
                    "type": "uint256"
                },
                {
                    "name": "_requiredGas",
                    "type": "uint256"
                },
                {
                    "name": "_requiredStackDepth",
                    "type": "uint16"
                },
                {
                    "name": "_basePayment",
                    "type": "uint256"
                },
                {
                    "name": "_baseDonation",
                    "type": "uint256"
                }
            ],
            "type": "constructor"
        }
    ]
