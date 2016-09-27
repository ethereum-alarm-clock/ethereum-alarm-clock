Execution
=========

.. contents:: :local:

.. class:: TransactionRequest
    :noindex:


.. warning:: 

    Anyone wishing to write their own execution client should be sure they fully
    understand all of the intricacies related to the execution of transaction
    requests.  The guarantees in place for those executing requests are only in
    place if the executing client is written appropriately.


Important Windows of Blocks/Time
--------------------------------


Freeze Window
^^^^^^^^^^^^^

Each request may specify a ``freezePeriod``.  This defines a number of blocks
or seconds prior to the ``windowStart`` during which no actions may be
performed against the request.  This is primarily in place to provide some
level of guarantee to those executing the request.  For anyone executing
requests, once the request enters the ``freezePeriod`` they can know that it
will not be cancelled and that they can send the executing transaction without
fear of it being cancelled at the last moment before the execution window
starts.


The Execution Window
^^^^^^^^^^^^^^^^^^^^

The **execution window** is the range of blocks or timestamps during which the
request may be executed.  This window is defined as the range of blocks or
timestamps from ``windowStart`` till ``windowStart + windowSize``.

For example, if a request was scheduled with a ``windowStart`` of block 2100
and a ``windowSize`` of 255 blocks, the request would be allowed to be executed
on any block such that ``windowStart <= block.number <= windowStart +
windowSize``.  

As another example, if a request was scheduled with a ``windowStart`` of block 2100
and a ``windowSize`` of 0 blocks, the request would only be allowed to be
executed at block 2100.  

Very short ``windowSize`` configurations likely lower the chances of your
request being executed at the desired time since it is not possible to force a
transaction to be included in a specific block and thus the party executing
your request may either fail to get the transaction included in the correct
block *or* they may choose to not try for fear that their transaction will not
be included in the correct block and thus they will not recieve a reimbursment
for their gas costs.

Similarly, very short ranges of time for timestamp based calls may even make it
impossible to execute the call.  For example, if you were to specify a
``windowStart`` at 1480000010 and a ``windowSize`` of 5 seconds then the
request would only be executable on blocks whose ``block.timestamp`` satisfied
the conditions ``1480000010 <= block.timestamp <= 1480000015``.  Given that it
is entirely possible that no blocks are mined within this small range of
timestamps there would never be a valid block for your request to be executed. 

.. note:: 

    It is worth pointing out that actual size of the execution window will
    always be ``windowSize + 1`` since the bounds are inclusive.


Reserved Execution Window
^^^^^^^^^^^^^^^^^^^^^^^^^

Each request may specify a ``claimWindowSize`` which defines a number of blocks
or seconds at the beginning of the execution window during which the request
may only be executed by the address which has claimed the request.  Once this
window has passed the request may be executed by anyone.

.. note:: 

    If the request has not been claimed this window is treated no differently than
    the remainder of the execution window.

For example, if a request specifies a ``windowStart`` of block 2100, a
``windowSize`` of 100 blocks, and a ``reservedWindowSize`` of 25 blocks then in
the case that the request was claimed then the request would only be executable
by the claimer for blocks satisfying the condition ``2100 <= block.number <
2125``.

.. note::

    It is worth pointing out that unlike the *execution window* the *reserved
    execution window* is not inclusive of it's righthand bound.

If the ``reservedWindowSize`` is set to 0, then there will be no window of
blocks during which the execution rights are exclusive to the claimer.
Similarly, if the ``reservedWindowSize`` is set to be equal to the full size of
the *execution window* or ``windowSize + 1`` then there will be not window
after the *reserved execution window* during which execution can be triggered
by anyone.

The :class:`RequestFactory` will allow a ``reservedWindowSize`` of any value
from 0 up to ``windowSize`` + 1, however, it is highly recommended that you
pick a number around 16 blocks or 270 seconds, leaving at least the same amount
of time unreserved during the second portion of the *execution window*.  This
ensures that there is sufficient motivation for your call to be claimed because
the person claiming the call knows that they will have ample opportunity to
execute it when the *execution window* comes around.  Conversely, leaving at
least as much time unreserved ensures that in the event that your request is
claimed but the claimer fails to execute the request that someone else has
plenty of of time to fulfill the execution before the *execution window* ends.


The Execution Lifecycle
-----------------------

When the :method:`TransactionRequest.execute()` function is called the contract
goes through three main sections of logic which are referred to as a whole as
the *execution lifecycle*.

1. Validation: Handles all of the checks that must be done to ensure that all
   of the conditions are correct for the requested transaction to be executed.
2. Execution: The actual sending of the requested transaction.
3. Accounting: Computing and sending of all payments to the necessary parties.


Part 1: Validation
^^^^^^^^^^^^^^^^^^

During the validation phase all of the following validation checks must pass.


Check #1: Not already called
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Requires the ``wasCalled`` attribute of the transaction request to
be ``false``.


Check #2: Not Cancelled
~~~~~~~~~~~~~~~~~~~~~~~

Requires the ``isCancelled`` attribute of the transaction request to
be ``false``.


Check #3: Not before execution window
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Requires ``block.number`` or ``block.timestamp`` to be greater than or equal to
the ``windowStart`` attribute.


Check #4: Not after execution window
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Requires ``block.number`` or ``block.timestamp`` to be less than or equal to
``windowStart + windowSize``.


Check #5 and #6: Within the execution window and authorized
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* If the request is claimed
    * If the current time is within the *reserved execution window*
        * Requires that ``msg.sender`` to be the ``claimedBy`` address
    * Otherwise during the remainder of the *execution window*
        * Always passes.
* If the request is not claimed.
    * Always passes if the current time is within the *execution window*


Check #7: Stack Depth Check
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to understand this check you need to understand the problem it solves.
One of the more subtle attacks that can be executed against a requested
transaction is to force it to fail by ensuring that it will encounter the EVM
stack limit.  Without this check the executor of a transaction request could
force *any* request to fail by arbitrarily increasing the stack depth prior to
execution such that when the transaction is sent it encounters the maximum
stack depth and fails.  From the perspective of the :class:`TransactionRequest`
contract this sort of failure is indistinguishable from any other exception.

In order to prevent this, prior to execution, the :class:`TransactionRequest`
contract will ensure that the stack can be extended by a number of stack frames
equal to ``requiredStackDepth``.  This check passes if the stack can be
extended by this amount.

This check will be skipped if ``msg.sender == tx.origin`` since in this case it
is not possible for the stack to have been arbitrarily extended prior to
execution.


Check #8: Sufficient Call Gas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Requires that the current value of ``msg.gas`` be greater than or equal to the
``callGas`` attribute.


Part 2: Execution
^^^^^^^^^^^^^^^^^

The execution phase is very minimalistic.  It marks the request as having been
called and then dispatches the requested transaction, storing the success or
failure on the ``wasSuccessful`` attribute.


Part 3: Accounting
^^^^^^^^^^^^^^^^^^

The accounting phase accounts for all of the payments and reimbursements that
need to be sent.

The *donation* payment is the mechanism through which developers can earn a
return on their development efforts on the Alarm service.  For the *official*
scheduler deployed as part of the alarm service this defaults to 1% of the
default payment.  This value is multiplied by the *gas multiplier* (see
:ref:`gas-multiplier`) and sent to the ``donationBenefactor`` address.

Next the payment for the actual execution is computed.  The formula for this is
as follows:

    ``totalPayment = payment * gasMultiplier + gasUsed * tx.gasprice + claimDeposit``

The three components of the ``totalPayment`` are as follows.

* ``payment * gasMultiplier``: The actual payment for execution.
* ``gasUsed * tx.gasprice``: The reimbursement for the gas costs of execution.
  This is not going to exactly match the actual gas costs, but it will always
  err on the side of overpaying slightly for gas consumption.
* ``claimDeposit``:  If the request is not claimed this will be 0.  Otherwise,
  the ``claimDeposit`` is always given to the executor of the request.

After these payments have been calculated and sent, the ``Executed`` event is
logged, and any remaining ether that is not allocated to be paid to any party
is sent back to the address that scheduled the request.


.. _gas-multiplier:

Gas Multiplier
--------------

To understand the *gas multiplier* you must understand the problem it solves.

Transactions requests always provide a 100% reimbursment of gas costs.  This is
implemented by requiring the scheduler to provide sufficient funds up-front to
cover the future gas costs of their transaction.  Ideally we want the sender of
the transaction that executes the request to be motivated to use a ``gasPrice``
that is as low as possible while still allowing the transaction to be included
in a block in a timely manner.

A naive approach would be to specify a *maximum* gas price that the scheduler
is willing to pay.  This might be possible for requests that will be processed
a short time in the future, but for transactions that are scheduled
sufficiently far in the future it isn't feasible to set a gas price that is
going to reliably reflect the current normal gas prices at that time.

In order to mitigate this issue, we instead provide a financial incentive to
the party executing the request to provide as low a gas cost as possible while
still getting their transaction included in a timely manner.

Those executing the request are already sufficiently motivated to provide a gas
price that is high enough to get the transaction mined in a reasonable time
since if the price they specify is too low it is likely that someone else will
execute the request before them, or that their transaction will not be included
before the *execution window* closes.

So, to provide incentive to keep the gas cost reasonably low, the *gas
multiplier* concept was introduced.  Simply put, the multiplier produces a
number between 0 and 2 which is applid to the ``payment`` that will be sent for
fulfilling the request.

At the time of scheduling, the ``gasPrice`` of the scheduling transaction is
stored.  We refer to this as the ``anchorGasPrice`` as we can assume with some
reliability that this value is a *reasonable* gas cost that the scheduler is
willing to pay.

At the time of execution, the following will occur based on the ``gasPrice``
used for the executing transaction:

    * If ``gasPrice`` is equal to the ``anchorGasPrice`` then the *gas
      multiplier* will be 1, meaning that the ``payment`` will be issued as is.
    * When the ``gasPrice`` is greater than the ``anchorGasPrice``, the *gas
      multiplier* will approach 0 meaning that the payment will steadily get
      smaller for higher gas prices.
    * When the ``gasPrice`` is less than the ``anchorGasPrice``, the *gas
      multiplier* will approach 2 meaning that the payment will steadily get
      larger for lower gas prices.

The formula used is the following.

* If the execution ``gasPrice`` is greater than ``anchorGasPrice``:
  
    ``gasMultiplier = anchorGasPrice / tx.gasprice``

* Else (if the execution ``gasPrice`` is less than or equal to the
  ``anchorGasPrice``:

    ``gasMultiplier = 2 - (anchorGasPrice / (2 * anchorGasPrice - tx.gasprice))``


For example, if at the time of scheduling the gas price was 100 wei and the
executing transaction uses a ``gasPrice`` of 200 wei, then the gas multiplier
would be ``100 / 200 => 0.5``.

Alternatively, if the transaction used a ``gasPrice`` of 75 wei then the gas
multiplier would be ``2 - (100 / (2 * 100 - 75)) => 1.2``.


Sending the Execution Transaction
---------------------------------

In addition to the pre-execution validation checks, the following things should
be taken into considuration when sending the executing transaction for a
request.


Gas Reimbursement
^^^^^^^^^^^^^^^^^

If the ``gasPrice`` of the network has increased significantly since the
request was scheduled it is possible that it no longer has sufficient ether to
pay for gas costs.  The following formula can be used to compute the maximum
amount of gas that a request is capable of paying:

    ``(request.balance - 2 * (payment + donation)) / tx.gasprice``

If you provide a gas value above this amount for the executing transaction then
you are not guaranteed to be fully reimbursed for gas costs.


Minimum ExecutionGas
^^^^^^^^^^^^^^^^^^^^

When sending the execution transaction, you should use the following rules to
determine the minimum gas to be sent with the transaction:

* Start with a baseline of the ``callGas`` attribute.
* Add ``180000`` gas to account for execution overhead.
* If you are proxying the execution through another contract such that during
  execution ``msg.sender != tx.origin`` then you need to provide an additional
  ``700 * requiredStackDepth`` gas for the stack depth checking.

For example, if you are sending the execution transaction directly from a
private key based address, and the request specified a ``callGas`` value of
120000 gas then you would need to provide ``120000 + 180000 => 300000`` gas.

If you were executing the same request, except the execution transaction was
being proxied through a contract, and the request specified a
``requiredStackDepth`` of 10 then you would need to provide ``120000 + 180000 +
700 * 10 => 307000`` gas.
