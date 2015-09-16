Scheduling
==========

Call scheduling is the core of the Ethereum Alarm Service.  Calls can be
scheduled on any block at least 40 blocks *(~10 minutes)* in the future.

Registering Call Data
---------------------

If a function call requires arguments, then prior to scheduling the call, the
call data for those arguments must be registered first.  This is done with the
``registerData`` function on the Alarm service.

* **Soldity Function Signature:** ``registerData()``
* **ABI Signature:** ``0xb0f07e44``

It may be confusing at first to see that this function does not take any
arguments, yet it is responsible for recording the call data for a future
function call.  Internally, the ``registerData`` function pulls the call data
off of ``msg.data``.

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


Scheduling the Call
-------------------

.. note::

    Prior to scheduling a function call, any call data necessary for the call must
    have already been registered.

Function calls are scheduled with the ``scheduleCall`` function on the Alarm
service.

* **Soldity Function Signature:** ``scheduleCall(address contractAddress, bytes4 signature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod, uint nonce) public returns (bytes32);``
* **ABI Signature:** ``0x52afbc33``

The ``scheduleCall`` function takes the following parameters:

* **address targetBlock:** The contract address that the function should be called on.
* **bytes4 signature:** The 4 byte ABI function signature for the call.
* **bytes32 dataHash:** The ``sha3`` hash of the call data for the call.
* **uint targetBlock:** The block number the call should be executed on.
* **uint8 gracePeriod:** The number of blocks after ``targetBlock`` that it is
  ok to still execute this call.
* **uint nonce:** Number to allow for differentiating a call from another one
  which has the exact same information for all other user specified fields.

Contract scheduling its own call
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Contracts can take care of their own call scheduling.

.. code-block::

    contract Lottery {
        address alarm; // set by some other mechanism.

        function beginLottery() public {
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

Alternatively, calls can be scheduled by one address to be executed on another
address.

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
    > sig = ... // the 4-byte ABI function signature for the wallet function that transfers funds.
    > targetBlock = eth.getBlock('latest') + 100  // 100 blocks in the future.
    > alarm.scheduleCall.sendTransaction(walletAddress, sig, dataHash, targetBlock, 255, 0, {from: eth.coinbase})

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

4. ``sig = ...``

    We also need to tell the Alarm service the 4 byte function signature it
    should use for the scheduled call.  Assuming our wallet's transfer function
    had a call signature of ``transferFunds(address to, uint value)`` then this
    value would be the result of
    ``bytes4(sha3(transferFunds(address,uint256))``.

5. ``targetBlock = eth.getBlock('latest') + 100``

6. ``alarm.scheduleCall.sendTransaction(walletAddress, sig, dataHash, targetBlock, 255, {from: eth.coinbase})``

    This is the actual line that schedules the function call.  We send a
    transaction using the ``scheduleCall`` function on the Alarm contract
    telling the Alarm service to schedule the call for 100 blocks in the future
    with the maximum grace period of 255 blocks, and a nonce of 0.

It should be noted that this example does not take into account any of the
authorization issues that would likely need to be in place such as restricting
the tranfer funds function to only accept authorized calls as well as
authorizing the desired addresses to make calls to the wallet address.
