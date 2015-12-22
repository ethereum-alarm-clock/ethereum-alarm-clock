Call Contract API
=================


Properties of a Call Contract
-----------------------------

A call contract for a scheduled call has the following publicly accessible
values.


* **address contractAddress:** the address of the contract the function should be called on.
* **address schedulerAddress:** the address who scheduled the call.
* **uint targetBlock:** the block that the function should be called on.
* **uint8 gracePeriod:** the number of blocks after the ``targetBlock`` during
  which it is stll ok to execute the call.
* **uint anchorGasPrice:** the gas price that was used when the call was
  scheduled.
* **uint suggestedGas:** a suggestion to the call executor as to how much gas
  the called function is expected to need.
* **uint basePayment:** the amount in wei that will be paid to the address that
  executes the function call.
* **uint baseFee:** the amount in wei that will be paid the creator of the
  Alarm service.
* **bytes4 abiSignature:** the 4 byte ABI function signature of the function on the
  ``contractAddress`` for this call.
* **bytes callData:** the data that will be passed to the called function.

* **bool wasCalled:** whether the call was called.
* **bool wasSuccessful:** whether the call was successful during execution.
* **bool isCancelled:** whether the call was cancelled.
* **address claimer:** the address that has claimed this contract.
* **uint claimAmount:** the amount that the claimer agreed to execute the contract for.
* **uint claimerDeposit:** the amount that the claimer has put up for deposit.


Contract Address
^^^^^^^^^^^^^^^^

**address contractAddress**

The address of the contract that the scheduled function call should be executed
on.  Retrieved with the ``contractAddress`` function.

* **Solidity Function Signature:** ``contractAddress() returns (address)``
* **ABI Signature:** ``0xf6b4dfb4``


Scheduler Address
^^^^^^^^^^^^^^^^^

**address schedulerAddress**

The address that the scheduled function call.  Retrieved with the
``schedulerAddress`` function.

* **Solidity Function Signature:** ``schedulerAddress() returns (address)``
* **ABI Signature:** ``0xae45850b``

Target Block
^^^^^^^^^^^^

**uint targetBlock**

The block number that this call should be executed on.  Retrieved with the
``targetBlock`` function.

* **Solidity Function Signature:** ``targetBlock() returns (uint)``
* **ABI Signature:** ``0xa16697a``


Grace Period
^^^^^^^^^^^^

**uint8 gracePeriod**

The number of blocks after the **targetBlock** that it is still ok to execute
this call.  Retrieved with the ``gracePeriod`` function.

* **Solidity Function Signature:** ``gracePeriod() returns (uint8)``
* **ABI Signature:** ``0xa06db7dc``


Anchor Gas Price
^^^^^^^^^^^^^^^^

**uint anchorGasPrice**

The value of ``tx.gasprice`` that was used to schedule this function call.
Retrieved with the ``anchorGasPrice`` function.

* **Solidity Function Signature:** ``anchorGasPrice() returns (uint)``
* **ABI Signature:** ``0x37f4c00e``


Suggested Gas
^^^^^^^^^^^^^

**uint suggestedGas**

A suggestion for the amount of gas that a caller should expect the called
function to require.  Retrieved with the ``suggestedGas`` function.

* **Solidity Function Signature:** ``suggestedGas() returns (uint)``
* **ABI Signature:** ``0x6560a307``


Base Payment
^^^^^^^^^^^^

**uint basePayment**

The base amount, in wei that the call executor's payment will be calculated
from. Retrieved with the ``basePayment`` function.

* **Solidity Function Signature:** ``basePayment() returns (uint)``
* **ABI Signature:** ``0xc6502da8``

Base Fee
^^^^^^^^

**uint baseFee**

The base amount, in wei that the fee to the creator of the alarm service will
be calculate from. Retrieved with the ``baseFee`` function.

* **Solidity Function Signature:** ``baseFee() returns (uint)``
* **ABI Signature:** ``0x6ef25c3a``


ABI Signature
^^^^^^^^^^^^^

**bytes4 abiSignature**

The ABI function signature that should be used to execute this function call.
Retrieved with the ``abiSignature`` function.

* **Solidity Function Signature:** ``abiSignature() returns (uint)``
* **ABI Signature:** ``0xca94692d``


Call Data
^^^^^^^^^

**bytes callData**

The full call data that will be used for this function call.  Retrieved
with the ``callData`` function.

* **Solidity Function Signature:** ``callData() returns (bytes)``
* **ABI Signature:** ``0x4e417a98``


Was Called
^^^^^^^^^^

**bool wasCalled**

Boolean as to whether this call has been executed.  Retrieved
with the ``wasCalled`` function.

* **Solidity Function Signature:** ``wasCalled() returns (bool)``
* **ABI Signature:** ``0xc6803622``


Was Successful
^^^^^^^^^^^^^^

**bool wasSuccessful**

Boolean as to whether this call was successful.  This indicates whether the
called contract returned without error.  Retrieved with the ``wasSuccessful``
function.

* **Solidity Function Signature:** ``wasSuccessful() returns (bool)``
* **ABI Signature:** ``0x9241200``


Is Cancelled
^^^^^^^^^^^^

**bool isCancelled**

Boolean as to whether this call has been cancelled. Retrieved with the
``isCancelled`` function.

* **Solidity Function Signature:** ``isCancelled() returns (bool)``
* **ABI Signature:** ``0x95ee1221``


Claimer
^^^^^^^

**address claimer**

Address of the account that has claimed this call for execution.  Retrieved
with the ``claimer`` function.

* **Solidity Function Signature:** ``claimer() returns (address)``
* **ABI Signature:** ``0xd379be23``


Claim Amount
^^^^^^^^^^^^

**uint claimAmount**

Ammount that the ``claimer`` has agreed to pay for the call. Retrieved with the
with the ``claimAmount`` function.

* **Solidity Function Signature:** ``claimAmount() returns (uint)``
* **ABI Signature:** ``0x830953ab``


Claim Deposit
^^^^^^^^^^^^^

**uint claimerDeposit**

Ammount that the ``claimer`` put down as a deposit. Retrieved with the
with the ``claimerDeposit`` function.

* **Solidity Function Signature:** ``claimerDeposit() returns (uint)``
* **ABI Signature:** ``0x3233c686``


Functions of a Call Contract
----------------------------

Cancel
^^^^^^

Cancels the scheduled call, suiciding the call contract and sending any funds
to the scheduler's address.  This function cannot be called from 265 blocks
prior to the **target block** for the call through the end of the grace period.

Before the call, only the scheduler may cancel the call.  Afterwards, anyone
may cancel it.

* **Solidity Function Signature:** ``cancel() public``
* **ABI Signature:** ``0xea8a1af0``


Execute
^^^^^^^

Triggers the execution of the call.  This can only be done during the window
between the ``targetBlock`` through the end of the ``gracePeriod``.  If the
call has been claimed, then only the claiming address can execute the call
during the first 16 blocks.  If the claming address does not execute the call
during this time, anyone who subsequently executes the call will receive their
deposit.

* **Solidity Function Signature:** ``execute() public``
* **ABI Signature:** ``0x61461954``
