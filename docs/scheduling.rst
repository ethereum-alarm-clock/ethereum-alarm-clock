Scheduling
==========

Call scheduling is the core of the Ethereum Alarm Service.  Calls can be
scheduled on any block at least 40 blocks *(~10 minutes)* in the future.

Properties of a Scheduled Call
------------------------------

* **address targetAddress:** the address of the contract the function should be called on.
* **address scheduledBy:** the address who scheduled the call.
* **uint calledAtBlock:** the block number on which the function was called.
  (``0`` if the call has not yet been executed.)
* **uint targetBlock:** the block that the function should be called on.
* **uint8 gracePeriod:** the number of blocks after the ``targetBlock`` during
  which it is stll ok to execute the call.
* **uint baseGasPrice:** the gas price that was used when the call was
  scheduled.
* **uint gasPrice:** the gas price that was used when the call was executed.
  (``0`` if the call has not yet been executed.)
* **uint gasUsed:** the amount of gas that was used to execute the function
  call (``0`` if the call has not yet been executed.)
* **uint payout:** the amount in wei that was paid to the address that executed
  the function call. (``0`` if the call has not yet been executed.)
* **uint fee:** the amount in wei that was kept to pay the creator of the Alarm
  service. (``0`` if the call has not yet been executed.)
* **bytes4 sig:** the 4 byte ABI function signature of the function on the
  ``targetAddress`` for this call.
* **bool isCancelled:** whether the call was cancelled.
* **bool wasCalled:** whether the call was called.
* **bool wasSuccessful:** whether the call was successful.
* **bytes32 dataHash:** the ``sha3`` hash of the data that should be used for
  this call.


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

* **Soldity Function Signature:** ``scheduleCall(address targetAddress, bytes4 signature, bytes32 dataHash, uint targetBlock, uint8 gracePeriod) public returns (bytes32);``
* **ABI Signature:** ``0x1145a20f``

The ``scheduleCall`` function takes the following parameters:

* **address targetBlock:** The contract address that the function should be called on.
* **bytes4 signature:** The 4 byte ABI function signature for the call.
* **bytes32 dataHash:** The ``sha3`` hash of the call data for the call.
* **uint targetBlock:** The block number the call should be executed on.
* **uint8 gracePeriod:** The number of blocks after ``targetBlock`` that it is
  ok to still execute this call.

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
            // 0x1145a20f is the ABI signature computed from `bytes4(sha3("scheduleCall(...)"))`.
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
