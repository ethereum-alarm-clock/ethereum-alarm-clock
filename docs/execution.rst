Call Execution
==============

Call execution is the process through which scheduled calls are executed at
their desired block number.  After a call has been scheduled, it can be executed
by account which chooses to initiate the transaction.  In exchange for
executing the scheduled call, they are paid a small fee of approximately 1% of
the gas cost used for executing the transaction.


Executing a call
----------------

Use the ``execute`` function to execute a scheduled call.  This function is
present on the call contract itself (as opposed to the scheduling service).

* **Solidity Function Signature:** ``execute() public``

When this function is called, the following things happen.

1. A few checks are done to be sure that all of the necessary pre-conditions
   pass.  If any fail, the function exits early without executing the scheduled
   call:

   * the call has not already been called.
   * the call has not been cancelled.
   * the transaction has at least ``requiredGas`` in gas.
   * the stack depth can be extended sufficiently deep for
     ``requiredStackDepth``
   * the current block number is within the range this call is allowed to be
     executed.
   * the caller is allowed to execute the function (see claiming)
2. The call is executed
3. The gas cost and fees are computed and paid.
4. The call contract sends any remaining funds to the scheduling
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

Each call contract has a ``requiredGas`` property.  Execution of a call
requires at least this amount of gas be sent with the transaction.

This gas value should be used in conjuction with the ``basePayment``
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

Since there may be multiple calls on the same block, it is best to also check
if the call has any *siblings* using the ``getNextCallSibling`` function.  This
function takes a call contract address and returns the address that is
scheduled to come next.

When checking for additional calls in this manner, you should check the target
block of each subsequent call to be sure it is within a range that you care
about.

* **Solidity Function Signature:** ``getNextCallSibling(address callAddress) returns (address)``

.. note::

    10 blocks into the future is a good range to monitor since new calls must
    always be scheduled at least 10 blocks in the future. 


The Freeze Window
-----------------

The 10 blocks prior to a call's target block are called the **freeze window**.  During this window, nothing about a call can change.  This means that it cannot be cancelled or claimed.


Claiming a call
---------------

Claiming a call is the process through which you as a call executor can
guarantee the exclusive right to execute the call during the first 16 blocks of
the call window for the scheduled call.  As part of the claim, you will need to
put down a deposit, which is returned to you if you when you execute the call.
Failing to execute the call will forfeit your deposit.


Claim Amount
^^^^^^^^^^^^

A call can be claimed during the 255 blocks prior to the freeze window.  This
period is referred to as the claim window.  The amount that you are agreeing to
be paid for the call is based on whichever block the call is claimed on.  The
amount can be calculated using the following formula.

* Let ``i`` be the index of the block within the 255 block claim window.
* Let ``basePayment`` be the payment amount specified by the call contract.
* If within the first 240 blocks of the window: ``payment = basePayment * i / 240``
* If within the last 15 blocks of the window: ``payment = basePayment``

This formula results in a linear growth from 0 to the full ``basePayment``
amount over the course of the first 240 blocks in the claim window.  The last
15 blocks are all set at the full ``basePayment`` amount.

A claim must be accompainied by a deposit that is at least twice the call's
``basePayment`` amount.


Getting your Deposit Back
^^^^^^^^^^^^^^^^^^^^^^^^^

If you claim a call and do not execute it within the first 16 blocks of the
call window, then you will risk losing your deposit.  Once the first 16 blocks
have passed, the call can be executed by anyone.  At this point, the first
person to execute the call will receive the deposit as part of their payment
(and incentive to pick up claimed calls that have not been called).


Claim API
^^^^^^^^^

To claim a contract

* **Solidity Function Signature:** ``claim()``

To check what the ``claimAmount`` will be for a given block number use the
``getClaimAmountForBlock`` function.  This will return an amount in wei that
represents the base payment value for the call if claimed on that block.

* **Solidity Function Signature:** ``getClaimAmountForBlock(uint blockNumber)``

This function also has a shortcut that uses the current block number

* **Solidity Function Signature:** ``getClaimAmountForBlock()``

You can check if a call has already been claimed with the ``claimer`` function.
This function will return either the empty address ``0x0`` if the call has not
been claimed, or the address of the claimer if it has.

* **Solidity Function Signature:** ``claimer() returns (address)``


Safeguards
----------

There are a limited set of safeguards that Alarm protects those executing calls
from.

* Ensures that the call cannot cause the executing transaction to fail due to
  running out of gas (like an infinite loop).
* Ensures that the funds to be used for payment are locked during the call
  execution.

Tips for executing scheduled calls
----------------------------------

The following tips may be useful if you wish to execute calls.

Look in the next 265 blocks
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Calls within this window are likely claimable.


Calls are frozen during the 10 blocks prior to the target block
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once a call enters the freeze window it is immutable until call execution.


No cancellation in next 265 blocks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Since calls cannot be cancelled less than 265 blocks in the future, you don't
need to check cancellation status during the 265 blocks prior to its target
block.


Check that it was not already called
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are executing a call after the target block but before the grace period
has run out, it is good to check that it has not already been called.


Compute how much gas to provide
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to guarantee that you will be 100% reimbursed for your gas
expenditures, then you need to compute how much gas the contract can pay for.
The *overhead* involved in execution is approximately 140,000 gas.  The
following formula should be a close approximation to how much gas a contract
can afford.

* let ``gasPrice`` be the gas price for the executing transaction.
* let ``balance`` be the ether balance of the contract.
* let ``claimerDeposit`` be the claimer's deposit amount.
* let ``basePayment`` be the base payment amount for the contract.  This may
  either be the value specified by the scheduler, or the ``claimAmount`` if the
  contract has been claimed.
* ``gas = (balance - 2 * basePayment - claimerDeposit) / gasPrice``
