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


* ``donationBenefactor``: ``0xd3cda913deb6f67967b99d67acdfa1712c293601`` which
  is the address of Piper Merriam, the creator of this project.
* ``claimWindowSize``: 255 blocks or 60 minutes
