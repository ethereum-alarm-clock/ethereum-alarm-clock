Scheduling
==========

Call scheduling is the core of the Ethereum Alarm Service.  Calls can be
scheduled on any block at least 40 blocks *(~10 minutes)* in the future.

When a call is scheduled, the service deploys a new contract that represents
the scheduled function call.  This contract is referred to as the **call
contract**. It holds all of the metadata associated with the call as well as
the funds that will be used to pay for the call.

Lifecycle of a Call Contract
----------------------------

* **creation** - The call contract is created as part of call scheduling.
* **pending** - The call can be cancelled anytime prior to the claim stage.
* **claim** - The contract can be claimed which will grant the claimer
  exclusive rights to execution during the first 16 blocks of the call window.
* **frozen** - The contract is frozen, preventing cancellation starting 10 blocks
  before the call's target block through the last block in the call window.
* **execution** - The executing transaction is sent, which triggers the call
  contract to execute the function call.
* **payment** - payments are sent to the executor and the creator of the alarm
  service.
* **finalization** - The contract sends any remaining funds to the address
  which scheduled the call.


Scheduling the Call
-------------------

Function calls are scheduled with the ``scheduleCall`` function on the Alarm
service.  This creates a new **call contract** that represents the function
call.  The primary signature for this function which accepts all allowed
configuration options is as follows.

.. code-block:: solidity

    function scheduleCall(address contractAddress,
                          bytes4 abiSignature,
                          bytes callData,
                          uint16 requiredStackDepth,
                          uint8 gracePeriod,
                          uint[5] args) public returns (address);

The ``uint[5] args`` is an array of 5 ``uint256`` values which are respectively
``callValue``, ``targetBlock``, ``requiredGas``, ``basePayment``,
``baseDonation``.


.. code-block:: solidity

    var (callValue, targetBlock, requiredGas, basePayment, baseDonation) = args;


There are a total of 10 available configuration options for a scheduled call.

* ``address contractAddress``
* ``bytes4 abiSignature``
* ``bytes callData``
* ``uint16 requiredStackDepth``
* ``uint8 gracePeriod``
* ``callValue``
* ``targetBlock``
* ``requiredGas``
* ``basePayment``
* ``baseDonation``


Call Configuration
^^^^^^^^^^^^^^^^^^


**address contractAddress:**

The address of the contract that the call should be called on.

* **Default:** ``msg.sender`` of the scheduling transaction.


**bytes4 abiSignature:**

The 4 byte ABI signature of the function to be called.

* **Default:** N/A.  If omitted this value is not used.

.. note::

    This configuration is a convenience feature.  It is perfectly fine to
    exclude this value and have the 4-byte function signature as part of the
    ``callData``.


**bytes callData:**

* **Default:** N/A. If omitted this value is not used.

.. note::

    If the abiSignature argument was specified then this should **not** include
    the 4-byte function signature.  Otherwise the call will be **double**
    prefixed with the function signature which is likely not what you want.


**uint callValue:**

The amount in wei that will be sent as part of call execution.

* **Default:** 0


**uint targetBlock:**

The block number the call should be executed on.  This must be at least 10
blocks in the future.

* **Default:** 10 blocks from the current block.


**uint8 gracePeriod:**

The number of blocks after ``targetBlock`` during which the call may still be
executed.  Cannot be less than 64 or greater than 255.

* **Default:** 255


**uint requiredGas:**

The amount of gas required to be sent along with the executing transaction.
This value cannot be less than 200,000 or more than the block gas limit minus
200,000 (``block.gaslimit - 200000``).

Call execution requires that at least this amount of gas be provided

* **Default:** 200,000.


**uint16 requiredStackDepth:**

The number of call stack frames should be checked prior to execution of the
function call cannot be less than 10 or greater than 1,000.  

If the call is being executed by another contract, call execution will verify
that the stack depth can be extended by this value.

* **Default:** 10


**uint basePayment:**

The base amount in wei that will be used to calculate the amount paid to the
executor of the call.

* **Default:** The current *market value* of a scheduled call.


**uint baseDonation:**

The base amount in wei that will be used to calculate the amount donated to the
creator of the service.


* **Default:** 1/100th of the current *market value* of a scheduled call.


Alternate Call Signatures
^^^^^^^^^^^^^^^^^^^^^^^^^


The ``scheduleCall`` function has many alternate call signatures that are
intended for simpler use in common use cases.

* ``scheduleCall()``

If called with no arguments then the scheduled call will execute a bare
``addr.call()`` where ``addr`` is the ``msg.sender`` from when the call was
scheduled.

* ``scheduleCall(bytes callData)``

In this case, the target of the call will be ``msg.sender`` from when the call
was scheduled, but the ``callData`` will be passed into the call
(``addr.call(callData)``)


* ``scheduleCall(bytes4 abiSignature)``

This is very similar to ``scheduleCall(bytes callData)`` except that it can
make it easy to execute a specific function that takes no arguments.


* ``scheduleCall(uint256 callValue, address contractAddress)``
* ``scheduleCall(address contractAddress, uint256 targetBlock, uint256 callValue)``

These signature can be used to easily schedule sending ether to another
address.


The exhaustive list of signatures for ``scheduleCall`` can be found below.

.. code-block::

    scheduleCall()
    scheduleCall(bytes callData)
    scheduleCall(uint256 targetBlock)
    scheduleCall(bytes4 abiSignature)
    scheduleCall(address contractAddress)
    scheduleCall(bytes4 abiSignature, bytes callData)
    scheduleCall(bytes4 abiSignature, uint256 targetBlock)
    scheduleCall(uint256 callValue, address contractAddress)
    scheduleCall(address contractAddress, bytes4 abiSignature)
    scheduleCall(address contractAddress, uint256 targetBlock)
    scheduleCall(bytes4 abiSignature, bytes callData, uint256 targetBlock)
    scheduleCall(address contractAddress, bytes4 abiSignature, bytes callData)
    scheduleCall(bytes4 abiSignature, uint256 targetBlock, uint256 requiredGas)
    scheduleCall(address contractAddress, uint256 callValue, bytes4 abiSignature)
    scheduleCall(address contractAddress, uint256 targetBlock, uint256 callValue)
    scheduleCall(address contractAddress, bytes4 abiSignature, uint256 targetBlock)
    scheduleCall(bytes4 abiSignature, bytes callData, uint256 targetBlock, uint256 requiredGas)
    scheduleCall(address contractAddress, bytes4 abiSignature, uint256 callValue, bytes callData)
    scheduleCall(bytes4 abiSignature, uint256 targetBlock, uint256 requiredGas, uint8 gracePeriod)
    scheduleCall(address contractAddress, bytes4 abiSignature, bytes callData, uint256 targetBlock)
    scheduleCall(address contractAddress, bytes4 abiSignature, uint256 targetBlock, uint256 requiredGas)
    scheduleCall(address contractAddress, bytes4 abiSignature, bytes callData, uint8 gracePeriod, uint256[4] args)
    scheduleCall(address contractAddress, bytes4 abiSignature, uint256 callValue, bytes callData, uint256 targetBlock)
    scheduleCall(bytes4 abiSignature, uint256 targetBlock, uint256 requiredGas, uint8 gracePeriod, uint256 basePayment)
    scheduleCall(address contractAddress, bytes4 abiSignature, bytes callData, uint256 targetBlock, uint256 requiredGas)
    scheduleCall(address contractAddress, bytes4 abiSignature, uint256 targetBlock, uint256 requiredGas, uint8 gracePeriod)
    scheduleCall(bytes4 abiSignature, bytes callData, uint256 targetBlock, uint256 requiredGas, uint8 gracePeriod, uint256 basePayment)
    scheduleCall(address contractAddress, bytes4 abiSignature, bytes callData, uint256 targetBlock, uint256 requiredGas, uint8 gracePeriod)
    scheduleCall(address contractAddress, bytes4 abiSignature, bytes callData, uint16 requiredStackDepth, uint8 gracePeriod, uint256[5] args)
    scheduleCall(address contractAddress, uint256 callValue, bytes4 abiSignature, uint256 targetBlock, uint256 requiredGas, uint8 gracePeriod)
    scheduleCall(address contractAddress, bytes4 abiSignature, uint256 targetBlock, uint256 requiredGas, uint8 gracePeriod, uint256 basePayment)
    scheduleCall(address contractAddress, bytes4 abiSignature, bytes callData, uint256 targetBlock, uint256 requiredGas, uint8 gracePeriod, uint256 basePayment)
    scheduleCall(address contractAddress, uint256 callValue, bytes4 abiSignature, uint256 targetBlock, uint256 requiredGas, uint8 gracePeriod, uint256 basePayment)
    scheduleCall(bytes4 abiSignature, bytes callData, uint16 requiredStackDepth, uint8 gracePeriod, uint256 callValue, uint256 targetBlock, uint256 requiredGas, uint256 basePayment, uint256 baseDonation)


Call Contract Address
^^^^^^^^^^^^^^^^^^^^^

Since each scheduled call is deployed as a standalone contract it can be useful
to have the address for the call contract.

If the ``scheduleCall`` function is being used from within a contract, the
address of the newly created call contract is returned.  If instead, the
function is being called directly in a transaction, the address of the call
contract can be extracted from the transaction logs under the ``CallScheduled``
event.


Contract scheduling its own call
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Contracts can take care of their own call scheduling.

.. code-block:: solidity

    contract Lottery {
        address scheduler; // set by some other mechanism.

        function beginLottery() public {
            ... // Do whatever setup needs to take place.

            // Now we schedule the picking of the winner.

            // the 4-byte signature of the local function we want to be called.
            bytes4 sig = bytes4(sha3("pickWinner()"));

            // approximately 24 hours from now
            uint targetBlock = block.number + 5760;

            // the 4-byte signature of the scheduleCall function.
            bytes4 scheduleCallSig = bytes4(sha3("scheduleCall(bytes4,uint256)"));

            scheduler.call(scheduleCallSig, sig, targetBlock)
        }

        function pickWinner() public {
            ...
        }
    }


In this example ``Lottery`` contract, every time the ``beginLottery`` function
is called, a call to the ``pickWinner`` function is scheduled for approximately
24 hours later (5760 blocks).


Upfront Payment
---------------

The service requires that you pay upfront for all costs associated with call
scheduling.  This value is referred to as the **endowment**.  Without intimate
knowledge of how all of these things are calculated it can be difficult to
determine how much to send.

One nice part about the service is that you can just send extra and anything
unused will be returned to you.  This is generally a good strategy since you
are at no risk of losing your ether and it prevents situations where you come
in slightly under the required endowment and have your call rejected.

The following functions are available to assist in computing this ether value.

* ``getMinimumEndowment() constant returns (uint)``
* ``getMinimumEndowment(uint basePayment) constant returns (uint)``
* ``getMinimumEndowment(uint basePayment, uint baseDonation) constant returns (uint)``
* ``getMinimumEndowment(uint basePayment, uint baseDonation, uint callValue) constant returns (uint)``
* ``getMinimumEndowment(uint basePayment, uint baseDonation, uint callValue, uint requiredGas) constant returns (uint)``



Call Data
---------

If a function call requires arguments then you have two options available.

* Provide the ``bytes`` as the ``callData`` argument at the time of scheduling.
* Register the ``bytes`` after the call has already been scheduled.

The call contract allows for call data registration via two mechanisms.  The
primary mechanism is through the fallback function on the contract.  This will
set the call data as the full call data of the transaction.

For example, if you were registering the call data for a function with the
signature ``myFunction(uint count, bytes32 reason)`` you could do it with the
following solidity code.

.. code-block:: solidity

    address scheduler = 0x...;
    // schedule the call
    address callContract = scheduler.call(...);

    // Register the call data
    scheduler.call(12345, 'abcde');


Alternatively you can use the ``registerData()`` function which will strip the
first four bytes off of ``msg.data`` and use the remainder as the call data.

In solidity, this would look something like the following.

.. code-block:: solidity

    contract Example {
        function doDataRegistration() public {
            uint arg1 = 3;
            int arg2 = -1;
            to.call(bytes4(sha3("registerData()")), arg1, arg2);
        }
    }

Once data has been registered, it cannot be modified.  Attempts to do so will
result in an exception.


.. note::

    The ``call()`` function on an address in solidity does not do any ABI encoding,
    so in cases where a scheduled call must pass something like a ``bytes``
    variable, you will need to handle the ABI encoding yourself.


Cancelling a call
-----------------

A scheduled call can be cancelled by its scheduler either before the claim
window begins.

* **Solidity Function Signature:** ``cancel()``

This will cause the call to be set as **cancelled**, which will return any
funds currently being held by the contract.

A call may also be cancelled after the call window if it has not been executed.


Looking up a Call
-----------------

You can lookup whether a particular address is a known scheduled call with the
``isKnownCall`` function.

* **Solidity Function Signature:** ``isKnownCall(address callAddress) returns (bool)``

Returns a boolean as to whether this address represents a known scheduled call.


Helper Functions
----------------

The following getters can be used to return the constant values that are used
by the service programatically.

* ``callAPIVersion() constant returns (uint)``

Returns the version of the Alarm service.

* ``getMinimumGracePeriod() constant returns (uint)``

The smallest value allowed for the ``gracePeriod`` of a scheduled call.

* ``getDefaultDonation() constant returns (uint)``

The default payment value for scheduled calls.

* ``getMinimumCallGas() constant returns (uint)``

The minimum allowed value for ``requiredGas``

* ``getMaximumCallGas() constant returns (uint)``

The maximum allowed value for ``requiredGas``.  This value is computed as
``block.gaslimit - getMinimumCallGas()``

* ``getDefaultRequiredGas() constant returns (uint)``

The default value for ``requiredGas``

* ``isKnownCall(address callAddress) constant returns (bool)``

Returns whether this address was a call contract that was deployed by the alarm
service.  This can be useful if you need to use the service to interact with
priviledged functions as you can verify that the address that is calling you is
in fact a legitimate call contract.

* ``getFirstSchedulableBlock() constant returns (uint)``

Returns the earliest block number in the future on which a call may be scheduled.

* ``getMinimumStackCheck() constant returns (uint16)``

The minimum allowed value for ``requiredStackDepth``.

* ``getMaximumStackCheck() constant returns (uint16)``

The maximum allowed value for ``requiredStackDepth``.

* ``getDefaultStackCheck() constant returns (uint16)``

The default value for the ``requiredStackDepth`` of a scheduled call.

* ``getDefaultGracePeriod() constant returns (uint8)``

The default value for the ``gracePeriod`` of a scheduled call.
