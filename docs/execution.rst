Execution
=========

.. contents:: :local:

.. class:: TransactionRequest


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
-------------------------

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
