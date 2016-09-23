Architecture
============

.. contents:: :local:


Overview
--------

The Alarm service is made of four main contracts.

* :class:`TransactionRequest`: Represents a single scheduled transaction.
* :class:`RequestFactory`: Low level API for creating :class:`TransactionRequest` contracts.
* :class:`RequestTracker`: Tracks the scheduled transactions.
* :class:`BlockScheduler`: High level API for creating :class:`TransactionRequest`
  contracts configured to be executed at a specified block number.
* :class:`EpochScheduler`: High level API for creating :class:`TransactionRequest`
  contracts configured to be executed at a specified time as specified by a timestamp.


BlockScheduler
--------------


