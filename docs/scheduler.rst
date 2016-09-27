Request Factory
===============

.. contents:: :local:

.. class:: Scheduler


Introduction
------------

The :class:`Scheduler` contract is the high level API for scheduling
transaction requests.  It exposes a very minimal subset of the full parameters
that can be specified for a :class:`TransactionRequest` in order to provide a
simplified scheduling API with fewer foot-guns.

The Alarm service exposes two schedulers.

* :class:`BlockScheduler` for block based scheduling.
* :class:`TimestampScheduler` for timestamp based scheduling.

Both of these contracts present an identical API.  The only difference is which
``temporalUnit`` that each created :class:`TransactionRequest` contract is
configured with.


Interface
---------

.. literalinclude:: ../contracts/SchedulerInterface.sol
    :language: solidity


Defaults
--------

The following defaults are used when creating a new :class:`TransactionRequest`
contract via either :class:`Scheduler` contract.


* ``donationBenefactor``: ``0xd3cda913deb6f67967b99d67acdfa1712c293601`` which
  is the address of Piper Merriam, the creator of this project.
* ``payment``: ``1000000 * tx.gasprice`` set at the time of scheduling.
* ``donation``: ``10000 * tx.gasprice`` or 1/100th of the default payment.
* ``reservedWindowSize``: 16 blocks or 5 minutes.
* ``freezePeriod``: 10 blocks or 3 minutes
* ``claimWindowSize``: 255 blocks or 60 minutes.
* ``requiredStackDepth``: 10 stack frames.


API
---

There are two ``scheduleTransaction`` methods on each :class:`Scheduler`
contract with different call signatures.


.. method:: Scheduler.scheduleTransaction(address toAddress, bytes callData, uint[4] uintArgs) returns (address)

This method allows for configuration of the most common parameters needed for
transaction scheduling.  Due to EVM restrictions, all of the unsigned integer
arguments are passed in as an array.  The array values are mapped to the
:class:`TransactionRequest` attributes as follows.

* ``uintArgs[0] => callGas``
* ``uintArgs[1] => callValue``
* ``uintArgs[2] => windowSize``
* ``uintArgs[3] => windowStart``


.. method:: Scheduler.scheduleTransaction(address toAddress, bytes callData, uint[4] uintArgs) returns (address)

This method presents three extra fields allowing more fine controll for
transaction scheduling.  Due to EVM restrictions, all of the unsigned integer
arguments are passed in as an array.  The array values are mapped to the
:class:`TransactionRequest` attributes as follows.

*  ``uintArgs[0] => callGas``
*  ``uintArgs[1] => callValue``
*  ``uintArgs[2] => donation``
*  ``uintArgs[3] => payment``
*  ``uintArgs[4] => requiredStackDepth``
*  ``uintArgs[5] => windowSize``
*  ``uintArgs[6] => windowStart``


Endowments
----------

When scheduling a transaction, you must provide sufficient ether to cover all
of the execution costs with some buffer to account for possible changes in the
network gas price.  See :ref:`endowment` for more information on how to compute
the endowment.
