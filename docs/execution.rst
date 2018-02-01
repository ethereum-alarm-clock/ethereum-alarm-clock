Execution
=========

.. contents:: :local:

.. class:: TransactionRequest
    :noindex:


.. warning:: 

    Anyone wishing to write their own execution client should be sure they fully
    understand all of the intricacies related to the execution of transaction
    requests.  The guarantees in place for those executing requests are only in
    place if the executing client is written appropriately. Reading this documentation
    is a good start.


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
transaction to be included in a specific block.  The party executing
your request may either fail to get the transaction included in the correct
block *or* they may choose to not try for fear that their transaction will not
be mined in the correct block, thereby not receiving their reimbursment
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


Check #8: Sufficient Call Gas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Requires that the current value of ``msg.gas`` be greater than the *minimum
call gas*.  See :ref:`minimum-call-gas` for details on how to compute this
value as it includes both the ``callGas`` amount as well as some extra for the
overhead involved in execution.


Part 2: Execution
^^^^^^^^^^^^^^^^^

The execution phase is very minimalistic.  It marks the request as having been
called and then dispatches the requested transaction, storing the success or
failure on the ``wasSuccessful`` attribute.


Part 3: Accounting
^^^^^^^^^^^^^^^^^^

The accounting phase accounts for all of the payments and reimbursements that
need to be sent.

The *fee* payment is the mechanism through which developers can earn a
return on their development efforts on the Alarm service.  When a person schedules 
a transaction they may choose to enter a ``fee`` amount which will get sent to 
the developer.  This value is multiplied by the *gas multiplier* (see
:ref:`gas-multiplier`) and sent to the ``feeRecipient`` address.

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

    ``(request.balance - 2 * (payment + fee)) / tx.gasprice``

If you provide a gas value above this amount for the executing transaction then
you are not guaranteed to be fully reimbursed for gas costs.


.. _minimum-execution-gas:

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
