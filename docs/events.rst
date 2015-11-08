Events
======

The following events are used to log notable events within the Alarm service.


Scheduler Events
----------------

The Scheduler contract logs the following events.


Call Scheduled
^^^^^^^^^^^^^^

* **Solidity Event Signature:** ``CallScheduled(address callAddress)``
* **ABI Signature:** ``0x2b05d346``

Logged when a new scheduled call is created. 


Call Rejected
^^^^^^^^^^^^^

* **Solidity Event Signature:** ``CallRejected(address indexed schedulerAddress, bytes32 reason)``
* **ABI Signature:** ``0x513485fc``

Logged when an attempt to schedule a function call fails.


Awarded Missed Block Bonus
^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Solidity Event Signature:** ``AwardedMissedBlockBonus(address indexed fromCaller, address indexed toCaller, uint indexed generationId, address callAddress, uint blockNumber, uint bonusAmount)``
* **ABI Signature:** ``0x1effaa2``

Executed anytime a pool member's bond is awarded to another address due to them
missing a scheduled call that was designated as theirs to execute.


Call Contract Events
--------------------

Each CallContract logs the following events.


Call Executed
^^^^^^^^^^^^^

* **Solidity Event Signature:** ``CallExecuted(address indexed executor, uint gasCost, uint payment, uint fee, bool success)``
        ;
* **ABI Signature:** ``0x4538b7ec``

Executed when the call is executed.


Call Aborted
^^^^^^^^^^^^

* **Solidity Event Signature:** ``_CallAborted(address executor, bytes32 reason)``
* **ABI Signature:** ``0xe92bb686``

Executed when an attempt is made to execute a scheduled call is rejected.  The
``reason`` value in this log entry contains a short string representation of
why the call was rejected.  (Note that this event name starts with an underscore)


Caller Pool Events
------------------

The following events are logged related to the caller pool.


Added To Generation
^^^^^^^^^^^^^^^^^^^

* **Solidity Event Signature:** ``_AddedToGeneration(address indexed callerAddress, uint indexed pool)``
* **ABI Signature:** ``0x4327115b``

Executed anytime a new address is added to the caller pool.


Removed From Generation
^^^^^^^^^^^^^^^^^^^^^^^

* **Solidity Event Signature:** ``_RemovedFromGeneration(address indexed callerAddress, uint indexed pool)``
* **ABI Signature:** ``0xd6940c8c``

Executed anytime an address is removed from the caller pool.
