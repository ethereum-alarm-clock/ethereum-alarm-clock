Architecture
============

.. contents:: :local:


Overview
--------

The Alarm service is made of the following contracts.

* :class:`TransactionRequest`: Represents a single scheduled transaction.
* :class:`RequestFactory`: Low level API for creating :class:`TransactionRequest` contracts.
* :class:`RequestTracker`: Tracks the scheduled transactions.
* :class:`BlockScheduler`: High level API for creating :class:`TransactionRequest`
  contracts configured to be executed at a specified block number.
* :class:`TimestampScheduler`: High level API for creating :class:`TransactionRequest`
  contracts configured to be executed at a certain time, as specified by a timestamp.

.. note:: 

    Actual functionality of most of the contracts is housed separately
    in various libraries.


.. class:: RequestTracker
    :noindex:

RequestTracker
--------------

The :class:`RequestTracker` is a database contract which tracks upcoming
transaction requests.  It exposes an API suitable for someone wishing to
execute transaction requests to be able to query which requests are scheduled
next as well as other common needs.

This database tracks requests based on the address that submits them.  This
allows the :class:`RequestTracker` to be un-permissioned allowing any address
to report scheduled transactions and to have them stored in their own personal
index.  The address which submits the transaction request is referred to as the
*scheduler address*.

This also enables those executing transaction requests to choose which
*scheduler addresses* they wish to execute transactions for.


.. class:: RequestFactory
    :noindex:

RequestFactory
--------------

The :class:`RequestFactory` contract is designed to be a low-level interface
for developers who need fine-grained control over all of the various
parameters that the :class:`TransactionRequest` can be configured with.

Parameter validation is available, but not mandatory.

It provides an API for creating new :class:`TransactionRequest` contracts.


.. class:: BlockScheduler
.. class:: TimestampScheduler

BlockScheduler and TimestampScheduler
-------------------------------------

The :class:`BlockScheduler` and :class:`TimestampScheduler` contracts are a
higher-level interface that most developers should want to use in order to
schedule a transaction for a future block or timestamp.

Both contracts present an identical API for creating new
:class:`TransactionRequest` contracts. Different from :class:`RequestFactory`,
request parameters are always validated.

:class:`BlockScheduler` treats all of the scheduling parameters as meaning
block numbers, while :class:`TimestampScheduler` treats them as meaning
timestamps and seconds.
