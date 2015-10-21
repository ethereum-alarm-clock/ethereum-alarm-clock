Events
======

The following events are used to log notable events within the Alarm service.


Alarm Events
------------

The primary Alarm service contract logs the following events.  Please not that
all of the event names begin with an underscore.


Deposit
^^^^^^^

* **Solidity Event Signature:** ``_Deposit(address indexed _from, address indexed accountAddress, uint value)``
* **ABI Signature:** ``0x47a08955``

Executed anytime a deposit is made into an address's Alarm account.


Withdraw
^^^^^^^^

* **Solidity Event Signature:** ``_Withdraw(address indexed accountAddress, uint value)``
* **ABI Signature:** ``0xd0c5cf41``

Executed anytime a withdrawl is made from an address's Alarm account.


Call Scheduled
^^^^^^^^^^^^^^

* **Solidity Event Signature:** ``CallScheduled(bytes32 indexed callKey)``
* **ABI Signature:** ``0xa951c534``

Executed when a new scheduled call is created. 


Call Executed
^^^^^^^^^^^^^

* **Solidity Event Signature:** ``CallExecuted(address indexed executedBy, bytes32 indexed callKey)``
* **ABI Signature:** ``0x8f4d8723``

Executed when a scheduled call is executed.


Call Aborted
^^^^^^^^^^^^

* **Solidity Event Signature:** ``CallAborted(address indexed executedBy, bytes32 indexed callKey, bytes18 reason)``
* **ABI Signature:** ``0xe92bb686``

Executed when an attempt is made to execute a scheduled call is rejected.  The
``reason`` value in this log entry contains a short string representation of
why the call was rejected.


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

Awarded Missed Block Bonus
^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Solidity Event Signature:** ``_AwardedMissedBlockBonus(address indexed fromCaller, address indexed toCaller, uint indexed poolNumber, bytes32 callKey, uint blockNumber, uint bonusAmount)``
* **ABI Signature:** ``0x7c41de34``

Executed anytime a pool member's bond is awarded to another address due to them
missing a scheduled call that was designated as theirs to execute.
