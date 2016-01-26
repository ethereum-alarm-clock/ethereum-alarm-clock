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
* **data-registered** - The data for the call is registered with the contract.
  This step can be skipped for function calls that take no arguments.
* **claiming** - The contract can be claimed which will grant the claimer
  exclusive rights to execution during the first 16 blocks of the call window.
* **locked** - The contract is locked, preventing cancellation starting 10 blocks
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
                          uint targetBlock,
                          uint requiredGas,
                          uint16 requiredStackDepth,
                          uint8 gracePeriod,
                          uint basePayment,
                          uint baseDonation) public returns (address);


Call Scheduling Arguments
^^^^^^^^^^^^^^^^^^^^^^^^^


**address contractAddress:**

The address of the contract that the call should be called on.

If omitted then ``msg.sender`` is used in it's place.


**bytes4 abiSignature:**

The 4 byte ABI signature of the function to be called.

If omitted then it is assumed that the ``callData`` is appropriately prefixed
with the function signature.  TODO: implement this.


**bytes callData:**

The call data that should be sent with the call.  

If omitted then it is assumed that the function should be called with no data.

.. note::

    If the abiSignature argument was specified then this should **not** include
    the 4-byte function signature.


**uint targetBlock:**

The block number the call should be executed on.  This must be at least 10
blocks in the future.

If omitted then the call will be scheduled for 10 blocks in the future.


**uint8 gracePeriod:**

The number of blocks after ``targetBlock`` during which the call may still be
executed.  Cannot be less than 64 or greater than 255.

If omitted the maximum value of 255 is used.


**uint requiredGas:**

The amount of gas required to be sent along with the executing transaction.

If omitted this defaults to 200,000.  TODO: implement this.


**uint16 requiredStackDepth:**

The number of call stack frames should be checked prior to execution of the
function call cannot be less than 10 or greater than 1,000.  Prior to call
execution the call contract will check that the stack can be extended by this
number.  If this fails then execution is aborted.

If omitted then this defaults to 10.  TODO: implement this


**uint basePayment:**

The base amount in wei that should be paid to the executor of the call.  When
validating that enough ether has been endowed to the call contract then the
maximum possible payment value of ``2 * basePayment`` is used.

If omitted this defaults to 1 ether.  TODO: fix this value


**uint baseDonation:**

The base amount in wei that should be donated to the creator of the service.


If omitted this defaults to 100 finney.  TODO: fix this value


Alternate Call Signatures
^^^^^^^^^^^^^^^^^^^^^^^^^


The ``scheduleCall`` function can be called with most any combination of these
arguments with the simplest version of this function being to call it with no
arguments (``scheduleCall()``) in which case the default values for each
argument are used.


The following alternative call signatures are also available for the
``scheduleCall`` function.


The optional arguments are implemented through the following alternate
invocation signatures.  The default value for each of the optional arguments
will be used if any of the following signatures are used.

* **Solidity Function Signature:** ``function scheduleCall(address contractAddress, bytes4 abiSignature, uint targetBlock) public returns (address)``
* **ABI Signature:** ``0x1991313``


* **Solidity Function Signature:** ``function scheduleCall(address contractAddress, bytes4 abiSignature, uint targetBlock, uint suggestedGas) public returns (address)``
* **ABI Signature:** ``0x49ae734``


* **Solidity Function Signature:** ``function scheduleCall(address contractAddress, bytes4 abiSignature, uint targetBlock, uint suggestedGas, uint8 gracePeriod) public returns (address)``
* **ABI Signature:** ``0x480b70bd``


* **Solidity Function Signature:** ``function scheduleCall(address contractAddress, bytes4 abiSignature, uint targetBlock, uint suggestedGas, uint8 gracePeriod, uint basePayment) public returns (address)``
* **ABI Signature:** ``0x68402460``

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
        address alarm; // set by some other mechanism.

        function beginLottery() public {
            ... // Do whatever setup needs to take place.

            // Now we schedule the picking of the winner.

            bytes4 sig = bytes4(sha3("pickWinner()"));
            // approximately 24 hours from now
            uint targetBlock = block.number + 5760;
            // 0x1991313 is the ABI signature computed from `bytes4(sha3("scheduleCall(...)"))`.
            alarm.call(0x1991313, address(this), sig, targetBlock)
        }

        function pickWinner() public {
            ...
        }
    }

In this example ``Lottery`` contract, every time the ``beginLottery`` function
is called, a call to the ``pickWinner`` function is scheduled for approximately
24 hours later (5760 blocks).


Scheduling a call for a contract
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, calls can be scheduled to be executed on other contracts

Lets look at an example where we want to schedule a funds transfer for a wallet
contract of some sort.

.. note::

    This example assuming that you have the Alarm contract ABI loaded into a
    web3 contract object.

.. code-block:: javascript

    // Now schedule the call
    > signature = ... // the 4-byte ABI function signature for the wallet function that transfers funds.
    > targetBlock = eth.getBlock('latest') + 100  // 100 blocks in the future.
    > alarm.scheduleCall.sendTransaction(walletAddress, signature, targetBlock, {from: eth.coinbase, value: web3.toWei(10, "ether")})


Registering Call Data
---------------------

If a function call requires arguments then it is up to the scheduler to
register the call data.  This needs to be done prior to execution.

The call contract allows for call data registration via two mechanisms.  The
primary mechanism is through the fallback function on the contract.  This will
set the call data as the full call data of the transaction.

.. code-block:: javascript

    // Register some call data
    > web3.eth.sendTransaction({to: scheduler.address, data: "0x...."})

Or, from within your contract.

.. code-block:: solidity

    contract Lottery {
        address alarm; // set by some other mechanism.

        function beginLottery() public {
            uint lotteryId = ...;

            // Now we schedule the picking of the winner.
            bytes4 sig = bytes4(sha3("pickWinner(uint256)"));
            // 0x1991313 is the ABI signature computed from `bytes4(sha3("scheduleCall(address,bytes4,uint256)"))`.
            alarm.call(0x1991313, address(this), sig, 100)

            // Register the call data
            alarm.call(lotteryId);
        }

        function pickWinner(uint lotteryId) public {
            ...
        }
    }


If however, your call data either has a ``bytes4`` value as it's first
argument, or, the first 4 bytes of the call data have a collision with one of
the existing function signatures on the call contract, you can use the
``registerData`` function instead.

* **Solidity Function Signature:** ``registerData()``
* **ABI Signature:** ``0xb0f07e44``


In solidity, this would look something like the following.

.. code-block::

    contract Example {
        function doDataRegistration() public {
            uint arg1 = 3;
            int arg2 = -1;
            to.call(bytes4(sha3("registerData()")), arg1, arg2);
        }
    }

Upon receiving this call, the Alarm service strips off the first four bytes
from ``msg.data`` to remove the ABI function signature and then stores the full
call data.

Once data has been registered, it cannot be modified.  Attempts to do so will
result in an exception.

ABI Encoding and address.call
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``call()`` function on an address in solidity does not do any ABI encoding,
so in cases where a scheduled call must pass something like a ``bytes``
variable, you will need to handle the ABI encoding yourself.


Cancelling a call
-----------------

A scheduled call can be cancelled by its scheduler up to 10 blocks
before it's target block.  To cancel a scheduled call use the ``cancel``
function.

* **Solidity Function Signature:** ``cancel()``
* **ABI Signature:** ``0xea8a1af0``

This will cause the call to be set as **cancelled**, which will return any
funds currently being held by the contract.


Looking up a Call
-----------------

You can lookup whether a particular address is a known scheduled call with the
``isKnownCall`` function.

* **Solidity Function Signature:** ``isKnownCall(address callAddress) returns (bool)``
* **ABI Signature:** ``0x523ccfa8``

Returns a boolean as to whether this address represents a known scheduled call.
