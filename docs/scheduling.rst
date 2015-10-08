Scheduling
==========

Call scheduling is the core of the Ethereum Alarm Service.  Calls can be
scheduled on any block at least 40 blocks *(~10 minutes)* in the future.

Registering Call Data
---------------------

If a function call requires arguments, then prior to scheduling the call, the
call data for those arguments must be registered.  This is done with the
``registerData`` function.

* **Solidity Function Signature:** ``registerData()``
* **ABI Signature:** ``0xb0f07e44``

It may be confusing at first to see that this function does not take any
arguments, yet it is responsible for recording the call data for a future
function call.  Internally, the ``registerData`` function pulls the call data
off of ``msg.data``, effectively allowing any number and type of arguments to
be passed to it (like the sha3 function).

In solidity, this would look something like the following.

.. code-block::

    contract Example {
        function doDataRegistration() public {
            uint arg1 = 3;
            int arg2 = -1;
            bytes arg3 = "some free form text";
            to.call(bytes4(sha3("registerData()")), arg1, arg2, arg3);
        }
    }

Upon receiving this call, the Alarm service strips off the first four bytes
from ``msg.data`` to remove the ABI function signature and then stores the full
call data.

Call data only ever needs to be registered once after which it can be used
without needing to re-register it.

The ``registerData`` function cannot be used via an abstract contract in
solidity, as solidity has not mechanism to allow for variadic arguments in a
function call.  You can however, simplify some of your contract code with a
local alias on your contract that handles the ``call`` logic for you.

.. code-block::

    contract Example {
        address alarm = 0x...;

        function registerData(uint arg1, int arg2, bytes arg3) public {
            // 0xb0f07e44 == bytes4(sha3("registerData()"))
            alarm.call(0xb0f07e44, arg1, arg2, arg3);
        }

        function scheduleIt() {
            registerData(1234, -1234, "some freeform text");
            ... // do remaining scheduling.
        }
    }

You can implement as many local ``registerData`` functions as you need with
each argument pattern that you need to schedule data for, allowing for simple
data registration.


Scheduling the Call
-------------------

Function calls are scheduled with the ``scheduleCall`` function on the Alarm
service.

* **Solidity Function Signature:** ``scheduleCall(address contractAddress, bytes4 signature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod, uint nonce);``
* **ABI Signature:** ``0x52afbc33``

The ``scheduleCall`` function takes the following parameters:

* **address contractAddress:** The contract address that the function should be
  called on.
* **bytes4 abiSignature:** The 4 byte ABI function signature for the call.
* **bytes32 dataHash:** The ``sha3`` hash of the call data for the call.
* **uint targetBlock:** The block number the call should be executed on.
* **uint8 gracePeriod:** The number of blocks after ``targetBlock`` that it is
  ok to still execute this call.
* **uint nonce:** Number to allow for differentiating a call from another one
  which has the exact same information for all other user specified fields.

.. note::

    Prior to scheduling a function call, any call data necessary for the call must
    have already been registered.

The ``scheduleCall`` function has two alternate invocation formats that can be
used as well.

* **Solidity Function Signature:** ``scheduleCall(address contractAddress, bytes4 abiSignature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod) public``
* **ABI Signature:** ``0x1145a20f``

When invoked this way, the **nonce** argument is defaulted to ``0``.


* **Solidity Function Signature:** ``scheduleCall(address contractAddress, bytes4 abiSignature, bytes32 dataHash, uint256 targetBlock) public``
* **ABI Signature:** ``0xf828c3fa``

When invoked this way, the **gracePeriod** argument is defaulted to ``255`` and
then **nonce** set to ``0``.


Contract scheduling its own call
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Contracts can take care of their own call scheduling.

.. code-block::

    contract Lottery {
        address alarm; // set by some other mechanism.

        function beginLottery() public {
            ... // Do whatever setup needs to take place.

            // Now we schedule the picking of the winner.

            bytes4 sig = bytes4(sha3("pickWinner()"));
            // `pickWinner()` takes no arguments so we send an empty sha3 hash.
            bytes32 dataHash = sha3();
            // approximately 24 hours from now
            uint targetBlock = block.number + 5760;
            // allow for the maximum grace period of 255 blocks.
            uint8 gracePeriod = 255;
            // 0x52afbc33 is the ABI signature computed from `bytes4(sha3("scheduleCall(...)"))`.
            alarm.call(0x1145a20f, address(this), sig, dataHash, targetBlock, gracePeriod)
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

.. note::

    The Alarm service operates under a *scheduler pays* model meaning that
    payment for all executed calls is taken from the scheduler's account.

Lets look at an example where we want to schedule a funds transfer for a wallet
contract of some sort.

.. note::

    This example assuming that you have the Alarm contract ABI loaded into a
    web3 contract object.

.. code-block:: javascript

    // First register the call data
    // 0xb0f07e44 is the ABI signature for the `registerData` function.
    > callData = ...  // the full ABI encoded call data for the call we want to schedule.
    > web3.sendTransaction({to: alarm.address, data: 'b0f07e44' + callData, from: eth.coinbase})
    // Now schedule the call
    > dataHash = eth.sha3(callData)
    > signature = ... // the 4-byte ABI function signature for the wallet function that transfers funds.
    > targetBlock = eth.getBlock('latest') + 100  // 100 blocks in the future.
    > alarm.scheduleCall.sendTransaction(walletAddress, signature, dataHash, targetBlock, 255, 0, {from: eth.coinbase})

There is a lot going on in this example so lets look at it line by line.

1. ``callData = ...``

    Our wallet contract will likely take some function arguments when
    transferring funds, such as the amount to be transferred.  This variable
    would need to be populated with the ABI encoded call data for this
    function.

2. ``web3.sendTransaction({to: alarm.address, data: 'b0f07e44' + callData, from: eth.coinbase})``

    Here we are registering the call data with the Alarm service.  ``b0f07e44``
    is the ABI encoded call signature for the ``registerData`` function on the
    alarm service.

3. ``dataHash = eth.sha3(callData)``

    Here we compute the ``sha3`` hash of the call data we will want sent with
    the scheduled call.

4. ``signature = ...``

    We also need to tell the Alarm service the 4 byte function signature it
    should use for the scheduled call.  Assuming our wallet's transfer function
    had a call signature of ``transferFunds(address to, uint value)`` then this
    value would be the result of
    ``bytes4(sha3(transferFunds(address,uint256))``.

5. ``targetBlock = eth.getBlock('latest') + 100``

    Schedule the call for 100 blocks in the future.

6. ``alarm.scheduleCall.sendTransaction(walletAddress, signature, dataHash, targetBlock, 255, 0, {from: eth.coinbase})``

    This is the actual line that schedules the function call.  We send a
    transaction using the ``scheduleCall`` function on the Alarm contract
    telling the Alarm service to schedule the call for 100 blocks in the future
    with the maximum grace period of 255 blocks, and a nonce of 0.

It should be noted that this example does not take into account any of the
authorization issues that would likely need to be in place such as restricting
the tranfer funds function to only accept authorized calls as well as
authorizing the desired addresses to make calls to the wallet address.

Cancelling a call
-----------------

A scheduled call can be cancelled by its scheduler up to 4 blocks (2 minutes)
before it's target block.  To cancel a scheduled call use the ``cancelCall``
function.

* **Solidity Function Signature:** ``cancelCall(bytes32 callKey)``
* **ABI Signature:** ``0x60b831e5``
