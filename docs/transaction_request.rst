Transaction Request
===================

.. contents:: :local:


.. class:: TransactionRequest

Each :class:`TransactionRequest` contract represents one transaction that has
been scheduled for future execution.  This contract is not intended to be used
directly as the :class:`RequestFactory` contract can be used to create new
:class:`TransactionRequest` contracts with full control over all of the
parameters.


Interface
---------

.. code-block:: solidity

    TODO: embed the actual interface contract here.


Data Model
----------

The data for the transaction request is split into 5 main sections.

* **Transaction Data**: Information specific to the execution of the transaction.
* **Payment Data**: Information related to the payment and donation associated
  with this request.
* **Claim Data**: Information about the claim status for this request.
* **Schedule Data**: Information about when this request should be executed.
* **Meta Data**: Information about the result of the request as well as which
  address owns this request and which address created this request.


Transaction Data
^^^^^^^^^^^^^^^^

This portion of the request data deals specifically with the transaction that
has been requested to be sent at a future block or time.  It has the following
fields.


.. attribute:: address toAddress

    The address that the transaction will be sent to.


.. attribute:: bytes callData

    The bytes that will be sent as the ``data`` section of the transaction.

.. attribute:: uint callValue

    The amount of ether, in wei, that will be sent with the transaction.


.. attribute:: uint callGas

    The amount of gas that will be sent with the transaction.

.. attribute:: uint requiredStackDepth

    The number of stack frames required by this transaction.


Payment Data
^^^^^^^^^^^^

Information surrounding the payment and donation for this request.


.. attribute:: uint anchorGasPrice

    The gas price that was used during creation of this request.  This is used
    to incentivise the use of an adequately low gas price during execution.

    TODO: Details on how this works.


.. attribute:: uint payment

    The amount of ether in wei that will be paid to the account that executes
    this transaction at the scheduled time.


.. attribute:: address paymentBenefactor

    The address that the payment will be sent to.  This is set during
    execution.


.. attribute:: uint paymentOwed

    The amount of ether in wei that is owed to the ``paymentBenefactor``. In
    most situations this will be zero at the end of execution, however, in the
    event that sending the payment fails the payment amount will be stored here
    and retrievable via the ``sendPayment()`` function.


.. attribute:: uint donation

    The amount of ether, in wei, that will be sent to the `donationBenefactor`
    upon execution.


.. attribute:: address donationBenefactor

    The address that the donation will be sent to.


.. attribute:: uint donationOwed

    The amount of ether in wei that is owed to the ``donationBenefactor``. In
    most situations this will be zero at the end of execution, however, in the
    event that sending the donation fails the donation amount will be stored here
    and retrievable via the ``sendDonation()`` function.


Claim Data
^^^^^^^^^^

Information surrounding the claiming of this request.  See :doc:`./claiming`
for more information.


.. attribute:: address claimedBy

    The address that has claimed this request.  If unclaimed this value will be
    set to the zero address ``0x0000000000000000000000000000000000000000``


.. attribute:: uint claimDeposit

    The amount of ether, in wei, that has been put down as a deposit towards
    claiming.  This amount is included in the payment that is sent during
    request execution.


.. attribute:: uint8 paymentModifier

    A number constrained between 0 and 100 (inclusive) which will be applied to
    the payment for this request.  This value is determined based on the time
    or block that the request is claimed.


Schedule Data
^^^^^^^^^^^^^

Information related to the window of time during which this request is
scheduled to be executed.


.. attribute:: uint temporalUnit

    Determines if this request is scheduled based on block numbers or timestamps.  
    
    * Set to ``1`` for block based scheduling.
    * Set to ``2`` for timestamp based scheduling.

    All other values are interpreted as being blocks or timestamps depending on
    what this value is set as.

.. attribute:: uint windowStart

    The block number or timestamp on which this request may first be executed.


.. attribute:: uint windowSize

    The number of blocks or seconds after the ``windowStart`` during which the
    request may still be executed.  This period of time is referred to as the
    *execution window*.  This period is inclusive of it's endpoints meaning
    that the request may be executed on the block or timestamp ``windowStart +
    windowSize``.

.. attribute:: uint freezePeriod

    The number of blocks or seconds prior to the ``windowStart`` during which
    no activity may occur.


.. attribute:: uint reservedWindowSize

    The number of blocks or seconds during the first portion of the the
    *execution window* during which the request may only be executed by the
    address that address that claimed the call.  If the call is not claimed,
    then this window of time is treated no differently.


.. attribute:: uint claimWindowSize

    The number of blocks prior to the ``freezePeriod`` during which the call
    may be claimed.


Meta Data
^^^^^^^^^

Information about ownership, creation, and the result of the transaction request.


.. attribute:: address owner

    The address that scheduled this transaction request.


.. attribute:: address createdBy

    The address that created this transaction request.  This value is set by
    the :class:`RequestFactory` meaning that if the request is *known* by the
    request factory then this value can be trusted to be the address that
    created the contract.  When using either the :class:`BlockScheduler` or
    :class:`TimestampScheduler` this address will be set to the respective
    scheduler contract..


.. attribute:: bool isCancelled

    Whether or not this request has been cancelled.


.. attribute:: bool wasCalled

    Whether or not this request was executed.


.. attribute:: bool wasSuccessful

    Whether or not the execution of this request returned ``true`` or
    ``false``.  In most cases this can be an indicator that an execption was
    thrown if set to ``false`` but there are also certain cases due to quirks
    in the EVM where this value may be ``true`` even though the call
    technically failed.


Actions
-------

The :class:`TransactionRequest` contract has three primary actions that can be performed.

* Cancellation: Cancels the request.
* Claiming: Reserves exclusive execution rights during a portion of the execution window.
* Execution: Sends the requested transaction.


Cancellation
^^^^^^^^^^^^

.. method:: TransactionRequest.cancel()

Cancellation can occur if either of the two are true.

* The current block or time is before the freeze period and the request has not
  been claimed.
* The current block or time is after the execution window and the request was
  not executed.

When cancelling prior to the execution window, only the ``owner`` of the call
may trigger cancellation.

When cancelling after the execution window, anyone may trigger cancellation.
To ensure that funds are not forever left to rot in these contracts, there is
an incentive layer for this function to be called by others whenever a request
fails to be executed.  When cancellation is executed by someone other than the
``owner`` of the contract, ``1%`` of what would have been paid to someone for
execution is paid to the account that triggers cancellation.


Claiming
--------

TODO
