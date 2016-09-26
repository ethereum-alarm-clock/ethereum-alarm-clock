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

Check #1: Insufficient Endowment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``result[0]``

Checks that the provided ``endowment`` is sufficient to pay for the donation
and payment as well as gas reimbursment.


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


.. method:: RequestFactory.createRequest(address[3] addressArgs, uint[11] uintArgs, bytes callData)

This function deploys a new :class:`TransactionRequest` contract.  This
function does not perform any validation and merely directly deploys the new
contract.


.. method:: RequestFactory.createValidatedRequest(address[3] addressArgs, uint[11] uintArgs, bytes callData)

This function first performs validation of the provided arguments and then
deploys the new :class:`TransactionRequest` contract when validation succeeds.

When validation fails, a ``ValidationError`` event will be logged for each
validation error that occured.
