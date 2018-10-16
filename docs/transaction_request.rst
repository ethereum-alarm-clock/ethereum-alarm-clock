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

.. literalinclude:: ../contracts/Interface/TransactionRequestInterface.sol
    :language: solidity


Events
------


.. method:: TransactionRequest.Cancelled(uint rewardPayment, uint measuredGasConsumption)

When a request is cancelled, the ``Cancelled`` event will be logged.  The
``rewardPayment`` is the amount that was paid to the party that cancelled the
request.  This will always be 0 when the owner of the request cancels the
request.


.. method:: TransactionRequest.Claimed()

When a request is claimed this event is logged.


.. method:: TransactionRequest.Aborted(uint8 reason);

When an attempt is made to execute a request but one of the pre-execution
checks fails, this event is logged.  The ``reason`` is an error code which maps
to the following errors.

* ``0 => WasCancelled``
* ``1 => AlreadyCalled``
* ``2 => BeforeCallWindow``
* ``3 => AfterCallWindow``
* ``4 => ReservedForClaimer``
* ``5 => InsufficientGas``
* ``6 => MismatchGasPrice``


.. method:: TransactionRequest.Executed(uint payment, uint fee, uint measuredGasConsumption)


When a request is successfully executed this event is logged.  The ``payment``
is the total payment amount that was awarded for execution.  The ``fee``
is the amount that was awarded to the ``feeRecipient``.  The
``measuredGasConsumption`` is the amount of gas that was reimbursed which
should always be slightly greater than the actual gas consumption.


Data Model
----------

The data for the transaction request is split into 5 main sections.

* **Transaction Data**: Information specific to the execution of the transaction.
* **Payment Data**: Information related to the payment and fee associated
  with this request.
* **Claim Data**: Information about the claim status for this request.
* **Schedule Data**: Information about when this request should be executed.
* **Meta Data**: Information about the result of the request as well as which
  address owns this request and which address created this request.


Retrieving Data
^^^^^^^^^^^^^^^

The data for a request can be retrieved using two methods.

.. method:: TransactionRequest.requestData()

This function returns the  serialized request data (excluding the ``callData``)
in a compact format spread across four arrays.  The data is returned
alphabetical, first by type, and then by section, then by field.

The return value of this function is four arrays.

* ``address[6] addressValues``
* ``bool[3] boolValues``
* ``uint256[15] uintValues``
* ``uint8[1] uint8Values``

These arrays then map to the following data fields on the request.

* Addresses (``address``)
    * ``addressValues[0] => claimData.claimedBy``
    * ``addressValues[1] => meta.createdBy``
    * ``addressValues[2] => meta.owner``
    * ``addressValues[3] => paymentData.feeRecipient``
    * ``addressValues[4] => paymentData.paymentBenefactor``
    * ``addressValues[5] => txnData.toAddress``

* Booleans (``bool``)
    * ``boolValues[0] => meta.isCancelled``
    * ``boolValues[1] => meta.wasCalled``
    * ``boolValues[2] => meta.wasSuccessful``

* Unsigned 256 bit Integers (``uint`` aka ``uint256``)
    * ``uintValues[0]  => claimData.claimDeposit``
    * ``uintValues[1]  => paymentData.anchorGasPrice``
    * ``uintValues[2]  => paymentData.fee``
    * ``uintValues[3]  => paymentData.feeOwed``
    * ``uintValues[4]  => paymentData.payment``
    * ``uintValues[5]  => paymentData.paymentOwed``
    * ``uintValues[6]  => schedule.claimWindowSize``
    * ``uintValues[7]  => schedule.freezePeriod``
    * ``uintValues[8]  => schedule.reservedWindowSize``
    * ``uintValues[9]  => schedule.temporalUnit``
    * ``uintValues[10] => schedule.windowStart``
    * ``uintValues[11] => schedule.windowSize``
    * ``uintValues[12] => txnData.callGas``
    * ``uintValues[13] => txnData.callValue``
    * ``uintValues[14] => txnData.gasPrice``

* Unsigned 8 bit Integers (``uint8``)
    * ``uint8Values[0] => claimData.paymentModifier``


.. method:: TransactionRequest.callData()

Returns the ``bytes`` value of the ``callData`` from the request's transaction
data.


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

.. attribute:: uint gasPrice 

    The gas price required to send when executing the transaction.


Payment Data
^^^^^^^^^^^^

Information surrounding the payment and fee for this request.


.. attribute:: uint anchorGasPrice

    The gas price that was used during creation of this request.  This is used
    to incentivise the use of an adequately low gas price during execution.

    See :ref:`gas-multiplier` for more information on how this is used.


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


.. attribute:: uint fee

    The amount of ether, in wei, that will be sent to the `feeRecipient`
    upon execution.


.. attribute:: address feeRecipient

    The address that the fee will be sent to.


.. attribute:: uint feeOwed

    The amount of ether in wei that is owed to the ``feeRecipient``. In
    most situations this will be zero at the end of execution, however, in the
    event that sending the fee fails the fee amount will be stored here
    and retrievable via the ``sendFee()`` function.


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

The :class:`TransactionRequest` contract has three primary actions that can be performed and 
a fourth action, `proxy`, which will be called in certain circumstances.

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
^^^^^^^^

.. method:: TransactionRequest.claim()

Claiming may occur during the ``claimWindowSize`` number of blocks or seconds
prior to the freeze period.  For example, if a request was configured as
follows:

* ``windowStart``: block #500
* ``freezePeriod``: 10 blocks
* ``claimWindowSize``: 100 blocks

In this case, the call would first be claimable at block 390.  The last block
in which it could be claimed would be block 489.

See the :doc:`./claiming` section of the documentation for details
about the claiming process.


Execution
^^^^^^^^^

.. method:: TransactionRequest.execute()

Execution may happen beginning at the block or timestamp denoted by the
``windowStart`` value all the way through and including the block or timestamp
denoted by ``windowStart + windowSize``.

See the :doc:`./execution` section of the documentation for details about the
execution process.

Proxy 
^^^^^

.. method:: TransactionRequest.proxy(address _to, bytes _data)

Proxy can only be called by the user who scheduled the TransactionRequest and
only after the execution window has passed. It exposes two fields, `_to` which will 
be the address of that the call will send to, and `_data` which is the encoded data 
to be sent with the transaction. The purpose of this function is to call another 
contract to do things like for example, transfer tokens. In the case a user schedules 
a call to buy from an ICO with the EAC, they will need to proxy call the token contract 
after the execution in order to move the tokens they bought out of the TransactionRequest 
contract.


Retrieval of Ether
------------------

All payments are automatically returned as part of normal request execution and
cancellation.  Since it is possible for these payments to fail, there are
backup methods that can be called individually to retrieve these different
payment or deposit values.

All of these functions may be called by anyone.


Returning the Claim Deposit
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. method:: TransactionRequest.refundClaimDeposit()

This method will return the claim deposit if either of the following conditions
are met.

* The request was cancelled.
* The execution window has passed.


Retrieving the Payment
^^^^^^^^^^^^^^^^^^^^^^^

.. method:: TransactionRequest.sendPayment()

This function will send the ``paymentOwed`` value to the
``paymentBenefactor``.  This is only callable after the execution window has
passed.


Retrieving the Fee
^^^^^^^^^^^^^^^^^^^^^^^

.. method:: TransactionRequest.sendFee()

This function will send the ``feeOwed`` value to the
``feeRecipient``.  This is only callable after the execution window has
passed.


Return any extra Ether
^^^^^^^^^^^^^^^^^^^^^^

This function will send any exta ether in the contract that is not owed as a
fee or payment and that is not part of the claim deposit back to the
``owner`` of the request.  This is only callable if one of the following
conditions is met.

* The request was cancelled.
* The execution window has passed.
