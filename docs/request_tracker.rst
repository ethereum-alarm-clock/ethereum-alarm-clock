Request Tracker
===============

.. contents:: :local:

.. class:: RequestTracker

Introduction
------------

The :class:`RequestTracker` contract is a simple database contract that exposes
an API suitable for querying for scheduled transaction requests.  This database
is *permissionless* in so much as it partitions transaction requests by the
address that reported them.  This means that *anyone* can deploy a new request
scheduler that conforms to whatever specific rules they may need for their use
case and configure it to report any requests it schedules with this tracker
contract.

Assuming that such a scheduler was written to still use the
:class:`RequestFactory` contract for creation of transaction requests, the
standard execution client will pickup and execute any requests that this
scheduler creates.


Interface
---------

.. literalinclude:: ../contracts/Interface/RequestTrackerInterface.sol
    :language: solidity


Database Structure
------------------

All functions exposed by the :class:`RequestTracker` take an ``address`` as the
first argument.  This is the address that reported the request into the
tracker.  This address is referred to as the *scheduling address* which merely
means that it is the address that reported this request into the tracker.  Each
*scheduling address* effectively receives it's own database.

All requests are tracked and ordered by their ``windowStart`` value.  The
tracker does not distinguish between block based scheduling and timestamp based
scheduling.

It is possible for a single :class:`TransactionRequest` contract to be listed
under multiple scheduling addresses since any address may report a request into
the database.


Chain of Trust
--------------

Since this database is permissionless, if you plan to consume data from it, you
should validate the following things.

* Check with the :class:`RequestFactory` that the ``request`` address is known
  using the :method:`RequestFactory.isKnownRequest()` function.
* Check that the ``windowStart`` attribute of the :class:`TransactionRequest`
  contract matches the registered ``windowStart`` value from the
  :class:`RequestTracker`.

Any request created by the :class:`RequestFactory` contract regardless of how
it was created should be safe to execute using the provided execution clients.


API
---


.. method:: RequestTracker.isKnownRequest(address scheduler, address request) constant returns (bool)

Returns ``true`` or ``false`` depending on whether this address has been
registered under this scheduler address.


.. method:: RequestTracker.getWindowStart(address scheduler, address request) constant returns (uint)

Returns the registered ``windowStart`` value for the request.  A return value
of 0 indicates that this address is not known.


.. method:: RequestTracker.getPreviousRequest(address scheduler, address request) constant returns (address)

Returns the address of the request who's ``windowStart`` comes directly before
this one.


.. method:: RequestTracker.getNextRequest(address scheduler, address request) constant returns (address)

Returns the address of the request who's ``windowStart`` comes directly after
this one.


.. method:: RequestTracker.addRequest(address request, uint startWindow) constant returns (bool)

Add an address into the tracker.  The ``msg.sender`` address will be used as
the *scheduler address* to determine which database to use.


.. method:: RequestTracker.removeRequest(address request) constant returns (bool)

Remove an address from the tracker.  The ``msg.sender`` address will be used as
the *scheduler address* to determine which database to use.


.. method:: RequestTracker.query(address scheduler, bytes2 operator, uint value) constant returns (address)

Query the database for the given scheduler.  Returns the address of the 1st
record which evaluates to ``true`` for the given query.

Allowed values for the ``operator`` parameter are:

* ``'>'``: For strictly greater than.
* ``'>='``: For greater than or equal to.
* ``'<'``: For strictly less than.
* ``'<='``: For less than or equal to.
* ``'=='``: For less than or equal to.

The ``value`` parameter is what the ``windowSize`` for each record will be
compared to.

If the return address is the null address
``0x0000000000000000000000000000000000000000`` then no records matched.
