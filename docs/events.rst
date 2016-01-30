Events
======

The following events are used to log notable events within the Alarm service.


Scheduler Events
----------------

The Scheduler contract logs the following events.


Call Scheduled
^^^^^^^^^^^^^^

* **Solidity Event Signature:** ``CallScheduled(address callAddress)``

Logged when a new scheduled call is created. 


Call Rejected
^^^^^^^^^^^^^

* **Solidity Event Signature:** ``CallRejected(address indexed schedulerAddress, bytes32 reason)``

Logged when an attempt to schedule a function call fails.


Call Contract Events
--------------------

Each CallContract logs the following events.


Call Executed
^^^^^^^^^^^^^

* **Solidity Event Signature:** ``CallExecuted(address indexed executor, uint gasCost, uint payment, uint fee, bool success)``
        ;

Executed when the call is executed.


Call Aborted
^^^^^^^^^^^^

* **Solidity Event Signature:** ``_CallAborted(address executor, bytes32 reason)``

Executed when an attempt is made to execute a scheduled call is rejected.  The
``reason`` value in this log entry contains a short string representation of
why the call was rejected.  (Note that this event name starts with an underscore)

Reasons:

    * ``NOT_ENOUGH_GAS`` - Executing transaction less than the ``requiredGas``
      value
    * ``ALREADY_CALLED`` - The call has already been executed.
    * ``NOT_IN_CALL_WINDOW`` - The transaction is occurring outside of the call
      window.
    * ``NOT_AUTHORIZED`` - Attempting to execute a claimed call during the
      period that the claimer has exclusive call rights.  * ``STACK_TOO_DEEP``
    * The stack depth could not be extended to ``requiredStackDepth``.
