Events
======

The following events are used to log notable events within the Alarm service.


Alarm Events
------------

The primary Alarm service contract logs the following events.


Deposit
^^^^^^^

* **Solidity Event Signature:** ``Deposit(address indexed _from, address indexed accountAddress, uint value)``
* **ABI Signature:** ``0x5548c837``

Executed anytime a deposit is made into an address's Alarm account.


Withdraw
^^^^^^^^

* **Solidity Event Signature:** ``Withdraw(address indexed accountAddress, uint value)``
* **ABI Signature:** ``0x884edad9``

Executed anytime a withdrawl is made from an address's Alarm account.


Call Scheduled
^^^^^^^^^^^^^^

* **Solidity Event Signature:** ``CallScheduled(bytes32 indexed callKey)``
* **ABI Signature:** ``0x5ca1bad5``

Executed when a new scheduled call is created. 


Call Executed
^^^^^^^^^^^^^

* **Solidity Event Signature:** ``CallExecuted(address indexed executedBy, bytes32 indexed callKey)``
* **ABI Signature:** ``0xed1062ba``

Executed when a scheduled call is executed.


Call Aborted
^^^^^^^^^^^^

* **Solidity Event Signature:** ``CallAborted(address indexed executedBy, bytes32 indexed callKey, bytes18 reason)``
* **ABI Signature:** ``0x84b46e45``

Executed when an attempt is made to execute a scheduled call is rejected.  The
``reason`` value in this log entry contains a short string representation of
why the call was rejected.


Caller Pool Events
------------------

The Caller Pool contract logs the following events.


Added To Pool
^^^^^^^^^^^^^

* **Solidity Event Signature:** ``AddedToPool(address indexed callerAddress, uint indexed pool)``
* **ABI Signature:** ``0xa192e48a``

Executed anytime a new address is added to the caller pool.


Removed From Pool
^^^^^^^^^^^^^^^^^

* **Solidity Event Signature:** ``RemovedFromPool(address indexed callerAddress, uint indexed pool)``
* **ABI Signature:** ``0xeee53013``

Executed anytime an address is removed from the caller pool.

Awarded Missed Block Bonus
^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Solidity Event Signature:** ``AwardedMissedBlockBonus(address indexed fromCaller, address indexed toCaller, uint indexed poolNumber, bytes32 callKey, uint blockNumber, uint bonusAmount)``
* **ABI Signature:** ``0x47d4e871``

Executed anytime a pool member's bond is awarded to another address due to them
missing a scheduled call that was designated as theirs to execute.
