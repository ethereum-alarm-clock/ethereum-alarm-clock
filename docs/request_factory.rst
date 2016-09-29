Request Factory
===============

.. contents:: :local:

.. class:: RequestFactory

Introduction
------------

The :class:`RequestFactory` contract is the lowest level API for creating
transaction requests.  It handles:

    * Validation and Deployment of :class:`TransactionRequest` contracts
    * Tracking of all addresses that it has deployed.

This contract is designed to allow tuning of all transaction parameters and is
probably the wrong API to integrate with if your goal is to simply schedule
transactions for later execution.  The :doc:`./scheduler` API is likely the
right solution for these use cases.


Interface
---------

.. literalinclude:: ../contracts/RequestFactoryInterface.sol
    :language: solidity


Events
------


.. method:: RequestFactory.RequestCreated(address request)

The ``RequestCreated`` event will be logged for each newly created
:class:`TransactionRequest`.


.. method:: RequestFactory.ValidationError(uint8 error)

The ``ValidationError`` event will be logged when an attempt is made to create
a new :class:`TransactionRequest` which fails due to validation errors.  The ``error`` represents an error code that maps to the following errors.


* ``0 => InsufficientEndowment``
* ``0 => ReservedWindowBiggerThanExecutionWindow``
* ``0 => InvalidTemporalUnit``
* ``0 => ExecutionWindowTooSoon``
* ``0 => InvalidRequiredStackDepth``
* ``0 => CallGasTooHigh``
* ``0 => EmptyToAddress``


Function Arguments
------------------

Because of the call stack limitations imposed by the EVM, all of the following
functions on the :class:`RequestFactory` contract take their arguments in the
form of the following form.  

* ``address[3] addressArgs``
* ``uint256[11] uintArgs``
* ``bytes callData``

The arrays map to to the following :class:`TransactionRequest` attributes.

* Addresses (``address``)
    * ``addressArgs[0] => meta.owner``
    * ``addressArgs[1] => paymentData.donationBenefactor``
    * ``addressArgs[2] => txnData.toAddress``

* Unsigned Integers (``uint`` aka ``uint256``)
    *  ``uintArgs[0]  => paymentData.donation``
    *  ``uintArgs[1]  => paymentData.payment``
    *  ``uintArgs[2]  => schedule.claimWindowSize``
    *  ``uintArgs[3]  => schedule.freezePeriod``
    *  ``uintArgs[4]  => schedule.reservedWindowSize``
    *  ``uintArgs[5]  => schedule.temporalUnit``
    *  ``uintArgs[6]  => schedule.windowStart``
    *  ``uintArgs[7]  => schedule.windowSize``
    *  ``uintArgs[8]  => txnData.callGas``
    *  ``uintArgs[9]  => txnData.callValue``
    *  ``uintArgs[10] => txnData.requiredStackDepth``


Validation
----------

.. method:: RequestFactory.validateRequestParams(address[3] addressArgs, uint[11] uintArgs, bytes callData, uint endowment) returns (bool[7] result)

The ``validateRequestParams`` function can be used to validate the parameters
to both ``createRequest`` and ``createValidatedRequest``.  The additional
parameter ``endowment`` should be the amount in wei that will be sent during
contract creation.

This function returns an array of ``bool`` values.  A ``true`` means that the
validation check succeeded.  A ``false`` means that the check failed.  The
``result`` array's values map to the following validation checks.


.. _endowment:

Check #1: Insufficient Endowment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``result[0]``

Checks that the provided ``endowment`` is sufficient to pay for the donation
and payment as well as gas reimbursment.

The required minimum endowment can be computed as the sum of the following:

* ``callValue`` to provide the ether that will be sent with the transaction.
* ``2 * payment`` to pay for maximum possible payment
* ``2 * donation`` to pay for maximum possible donation
* ``2 * callGas * tx.gasprice`` to pay for ``callGas`` with up to a 2x increase
  in the network gas price.
* ``2 * 700 * requiredStackDepth * tx.gasprice`` to pay gas for the stack depth
  checking with up to a 2x increase in network gas costs.
* ``2 * 180000 * tx.gasprice`` to pay for the gas overhead involved in
  transaction execution.


Check #2: Invalid Reserved Window
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``result[1]``

Checks that the ``reservedWindowSize`` is less than or equal to ``windowSize +
1``.


Check #3: Invalid Temporal Unit
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``result[2]``

Checks that the ``temporalUnit`` is either ``1`` to specify block based scheduling,
or ``2`` to specify timestamp based scheduling.


Check #4: Execution Window Too Soon
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``result[3]``

Checks that the current ``now`` value is not greater than ``windowStart -
freezePeriod``.

* When using block based scheduling, ``block.number`` is used for the ``now``
  value.
* When using timestamp based scheduling, ``block.timestamp`` is used.


Check #5: Invalid Stack Depth Check
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``result[4]``

Checks that the ``requiredStackDepth`` is less than or equal to 1000.


Check #6: Call Gas too high
^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``result[5]``

Check that the specified ``callGas`` value is not greater than the current
``gasLimit - 140000`` where ``140000`` is the gas overhead of request
execution.

Check #7: Empty To Address
^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``result[6]``

Checks that the ``toAddress`` is not the null address
``0x0000000000000000000000000000000000000000``.


Creation of Transaction Requests
--------------------------------


.. method:: RequestFactory.createRequest(address[3] addressArgs, uint[11] uintArgs, bytes callData) returns (address)

This function deploys a new :class:`TransactionRequest` contract.  This
function does not perform any validation and merely directly deploys the new
contract.

Upon successful creation the ``RequestCreated`` event will be logged.


.. method:: RequestFactory.createValidatedRequest(address[3] addressArgs, uint[11] uintArgs, bytes callData) returns (address)

This function first performs validation of the provided arguments and then
deploys the new :class:`TransactionRequest` contract when validation succeeds.

When validation fails, a ``ValidationError`` event will be logged for each
validation error that occured.


Tracking API
------------

.. method:: RequestFactory.isKnownRequest(address _address) returns (bool)

This method will return ``true`` if the address is a
:class:`TransactionRequest` that was created from this contract.
