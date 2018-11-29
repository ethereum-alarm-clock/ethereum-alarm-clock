Scheduler
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

.. literalinclude:: ../contracts/Interface/SchedulerInterface.sol
    :language: solidity


Defaults
--------

The following defaults are used when creating a new :class:`TransactionRequest`
contract via either :class:`Scheduler` contract.


* ``feeRecipient``: ``0xecc9c5fff8937578141592e7E62C2D2E364311b8`` which
  is the address of the developer contribution wallet, which is used to fund the project.
* ``payment``: ``1000000 * tx.gasprice`` set at the time of scheduling.
* ``fee``: ``10000 * tx.gasprice`` or 1/100th of the default payment.
* ``reservedWindowSize``: 16 blocks or 5 minutes.
* ``freezePeriod``: 10 blocks or 3 minutes
* ``claimWindowSize``: 255 blocks or 60 minutes.


API
---

There is just one ``schedule`` method on each :class:`Scheduler`
contract with different call signatures. (Prior versions of the EAC had 2 API methods, we 
reduced this down to only the full API to force specification of all parameters.)


.. method:: Scheduler.schedule(address _toAddress, bytes _callData, uint[7] _uintArgs) public payable returns (address newRequest)

The ``_toAddress`` is the recipient that the transaction will be sent to when it 
is executed. The recipient can be any valid Ethereum address including both 
user accounts and contracts. ``_callData`` is the encoded bytecode that will be sent 
with the transaction. Simple value transfers can set this variable to an empty string,
but more complex calls will need to encode the method of the inteded call and pass 
it in this variable.

The ``_uintArgs`` map to the following variables:

* ``_uintArgs[0]``: The ``callGas`` to be sent with the executing transaction.
* ``_uintArgs[1]``: The ``value`` in wei to be sent with the transaction.
* ``_uintArgs[2]``: The ``windowSize``, or size of the exeuction window.
* ``_uintArgs[3]``: The ``windowStart``, or the block / timestamp of when the execution window begins.
* ``_uintArgs[4]``: The ``gasPrice`` that must be sent with the executing transaction.
* ``_uintArgs[5]``: The ``fee`` value attached to the transaction.
* ``_uintArgs[6]``: The ``payment`` value attached to the transaction.

The method returns the ``address`` of the newly created :class:`TransactionRequest`.


Endowments
----------

When scheduling a transaction, you must provide sufficient ether to cover all
of the execution costs with some buffer to account for possible changes in the
network gas price.  See :ref:`endowment` for more information on how to compute
the endowment.
