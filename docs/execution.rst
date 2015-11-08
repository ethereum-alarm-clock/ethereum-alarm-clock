Call Execution
==============

Call execution is the process through which scheduled calls are executed at
their desired block number.  After a call has been scheduled, it can be executed
by account which chooses to initiate the transaction.  In exchange for
executing the scheduled call, they are paid a small fee of approximately 1% of
the gas cost used for executing the transaction.


Executing a call
----------------

Use the ``execute`` function to execute a scheduled call.

* **Solidity Function Signature:** ``execute(address callAddress)``
* **ABI Signature:** ``0xfcf36918``

When this function is called, the following things happen.

1. A few checks are done to be sure that all of the necessary pre-conditions
   pass.  If any fail, the function exits early without executing the scheduled
   call:

   * the call has not already been suicided
   * the current block number is within the range this call is allowed to be
     executed.
   * the caller is allowed to execute the function (see caller pool)
2. The call is executed
3. The gas cost and fees are computed and paid.
4. The call contract suicides, sending any remaining funds to the scheduling
   address.


Payment
^^^^^^^

Each scheduled call sets its own payment value.  This can be looked up with the
``basePayment`` accessor function.

The final payment value for executing the scheduled call is the ``basePayment``
multiplied by a scalar value based on the difference between the gas price of
the executing transaction and the gas price that was used to schedule the
transaction.  The formula for this scalar is such that the lower the gas price
of the executing transaction, the higher the payment.


Setting transaction gas and gas price
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each call contract has a ``suggestedGas`` property that can be used as a
suggestion for how much gas the function call needs.  In the case where this is
set to zero it means the scheduler has not provided a suggestion.

This suggested gas value should be used in conjuction with the ``basePayment``
and ``baseFee`` amounts with respect to the ether balance of the call contract.
The provided gas for the transaction should not exceed ``(balance - 2 *
(basePayment + baseFee)) / gasPrice`` if you want to guarantee that you will be
fully reimbursed for gas expenditures.


Getting your payment
^^^^^^^^^^^^^^^^^^^^

Payment for executing a call is sent to you as part of the executing
transaction, as well as being logged by the ``CallExecuted`` event.


Determining what scheduled calls are next
-----------------------------------------

You can query the Alarm service for the call key of the next scheduled call on
or after a specified block number using the ``getNextCall`` function

* **Solidity Function Signature:** ``getNextCall(uint blockNumber) returns (address)``
* **ABI Signature:** ``0x9f927be7``

Since there may be multiple calls on the same block, it is best to also check
if the call has any *siblings* using the ``getNextCallSibling`` function.  This
function takes a call contract address and returns the address that is
scheduled to come next.

When checking for additional calls in this manner, you should check the target
block of each subsequent call to be sure it is within a range that you care
about.

* **Solidity Function Signature:** ``getNextCallSibling(address callAddress) returns (address)``
* **ABI Signature:** ``0x48107843``

.. note::

    40 blocks into the future is a good range to monitor since new calls must
    always be scheduled at least 40 blocks in the future.  You should also
    monitor these functions up to 10 blocks before their target block to be
    sure they are not cancelled.


Designated Callers
------------------

If the Caller Pool has any bonded callers in the current active pool, then only
designated callers will be allowed to execute a scheduled call.  The exception
to this restriction is the last few blocks within the call's grace period which
the call enters *free-for-all* mode during which anyone may execute it.

If there are no bonded callers in the Caller Pool then the Alarm service will
operate in *free-for-all* mode for all calls meaning anyone may execute any
call at any block during the call window.

How callers designated
^^^^^^^^^^^^^^^^^^^^^^

Each call has a window during which it is allowed to be executed.  This window
begins at the specified ``targetBlock`` and extends through ``targetBlock +
gracePeriod``.   This window is inclusive of it's bounding blocks.

For each 16 block section of the call window, the caller pool associated with
the ``targetBlock`` is selected.  The members of the pool can be though of as a
circular queue, meaning that when you iterate through them, when you reach the
last member, you start back over at the first member.  For each call, a random
starting position is selected in the member queue and the 16 block sections of
the call window are assigned in order to the membes of the call pool beginning
at this randomly chosen index..

The last two 16 block sections (17-32 blocks depending on the gracePeriod) are not
allocated, but are considered *free-for-all* allowing anyone to call.

Use the ``getDesignatedCaller`` function to determine which caller from the
caller pool has been designated for the block.

* **Solidity Function Signature:** ``getDesignatedCaller(address callAddress, uint256 blockNumber) returns (bool, address)``
* **ABI Signature:** ``0x5a8dd79f``

* **callAddress:** specifies the address of the call contract.
* **blockNumber:** the block number (during the call window) in question.

This returns a boolean and an address.  The boolean designates whether this
scheduled call was designated (if there are no registered caller pool members
then all calls operate in free-for-all mode).  The address is the designated
caller.  If the returned address is ``0x0`` then this call can be executed by
anyone on the provided block number.

Missing the call window
^^^^^^^^^^^^^^^^^^^^^^^

Anytime a caller fails to execute a scheduled call during the 4 block window
reserved for them, the next caller has the opportunity to claim a portion of
their bond merely by executing the call during their window.  When this
happens, the previous caller who missed their call window has the current
minimum bond amount deducted from their bond balance and transferred to the
caller who executed the call.  The caller who missed their call is also removed
from the pool.  This removal takes 416 blocks to take place as it occurs within
the same mechanism as if they removed themselves from the pool.

Free For All
^^^^^^^^^^^^

When a call enters the last two 16-block chunks of its call window it enters
free-for-all mode.  During these blocks anyone, even unbonded callers, can
execute the call.  The sender of the executing transaction will be rewarded the
bond bonus from all callers who missed their call window.


Safeguards
----------

There are a limited set of safeguards that Alarm protects those executing calls
from.

* Enforces the ability to pay for the maximum possible transaction cost up
  front.
* Ensures that the call cannot cause the executing transaction to fail due to
  running out of gas (like an infinite loop).
* Ensures that the funds to be used for payment are locked during the call
  execution.

Tips for executing scheduled calls
----------------------------------

The following tips may be useful if you wish to execute calls.

Only look in the next 40 blocks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Since calls cannot be scheduled less than 40 blocks in the future, you can
count on the call ordering remaining static for the next 40 blocks.

No cancellation in next 8 blocks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Since calls cannot be cancelled less than 8 blocks in the future, you don't
need to check cancellation status during the 8 blocks prior to its target
block.

Check that it was not already called
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are executing a call after the target block but before the grace period
has run out, it is good to check that it has not already been called.

Check that the scheduler can pay
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is good to check that the scheduler has sufficient funds to pay for the
call's potential gas cost plus fees.
