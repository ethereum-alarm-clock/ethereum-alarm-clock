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
* **uint requiredGas:** the amount of gas that must be sent with the executing transaction.
* **uint basePayment:** the amount in wei that will be paid to the address that
  executes the function call.
* **uint baseFee:** the amount in wei that will be paid the creator of the
  Alarm service.
* **bytes4 abiSignature:** the 4 byte ABI function signature of the function on the
  ``contractAddress`` for this call.
* **bytes callData:** the data that will be passed to the called function.
* **bytes callValue:** the value in wei that will be sent with this call
* **uint16 requiredStackDepth:** the depth by which the stack must be
  increasable at the time of execution.

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


Scheduler Address
^^^^^^^^^^^^^^^^^

**address schedulerAddress**

The address that the scheduled function call.  Retrieved with the
``schedulerAddress`` function.

* **Solidity Function Signature:** ``schedulerAddress() returns (address)``


Target Block
^^^^^^^^^^^^

**uint targetBlock**

The block number that this call should be executed on.  Retrieved with the
``targetBlock`` function.

* **Solidity Function Signature:** ``targetBlock() returns (uint)``


Grace Period
^^^^^^^^^^^^

**uint8 gracePeriod**

The number of blocks after the **targetBlock** that it is still ok to execute
this call.  Retrieved with the ``gracePeriod`` function.

* **Solidity Function Signature:** ``gracePeriod() returns (uint8)``


Anchor Gas Price
^^^^^^^^^^^^^^^^

**uint anchorGasPrice**

The value of ``tx.gasprice`` that was used to schedule this function call.
Retrieved with the ``anchorGasPrice`` function.

* **Solidity Function Signature:** ``anchorGasPrice() returns (uint)``


Required Gas
^^^^^^^^^^^^

**uint requiredGas**

The amount of gas that must be sent with the executing transaction. Retrieved
with the ``requiredGas`` function.

* **Solidity Function Signature:** ``requiredGas() returns (uint)``


Base Payment
^^^^^^^^^^^^

**uint basePayment**

The base amount, in wei that the call executor's payment will be calculated
from. Retrieved with the ``basePayment`` function.

* **Solidity Function Signature:** ``basePayment() returns (uint)``

Base Fee
^^^^^^^^

**uint baseFee**

The base amount, in wei that the fee to the creator of the alarm service will
be calculate from. Retrieved with the ``baseFee`` function.

* **Solidity Function Signature:** ``baseFee() returns (uint)``


ABI Signature
^^^^^^^^^^^^^

**bytes4 abiSignature**

The ABI function signature that should be used to execute this function call.
Retrieved with the ``abiSignature`` function.

* **Solidity Function Signature:** ``abiSignature() returns (uint)``


Call Data
^^^^^^^^^

**bytes callData**

The full call data that will be used for this function call.  Retrieved
with the ``callData`` function.

* **Solidity Function Signature:** ``callData() returns (bytes)``


Call Value
^^^^^^^^^^

**uint callValue**

The amount in wei that will be sent with the function call.  Retrieved with the
``callValue`` function.

* **Solidity Function Signature:** ``callValue() returns (bytes)``


Was Called
^^^^^^^^^^

**bool wasCalled**

Boolean as to whether this call has been executed.  Retrieved
with the ``wasCalled`` function.

* **Solidity Function Signature:** ``wasCalled() returns (bool)``


Was Successful
^^^^^^^^^^^^^^

**bool wasSuccessful**

Boolean as to whether this call was successful.  This indicates whether the
called contract returned without error.  Retrieved with the ``wasSuccessful``
function.

* **Solidity Function Signature:** ``wasSuccessful() returns (bool)``


Is Cancelled
^^^^^^^^^^^^

**bool isCancelled**

Boolean as to whether this call has been cancelled. Retrieved with the
``isCancelled`` function.

* **Solidity Function Signature:** ``isCancelled() returns (bool)``


Claimer
^^^^^^^

**address claimer**

Address of the account that has claimed this call for execution.  Retrieved
with the ``claimer`` function.

* **Solidity Function Signature:** ``claimer() returns (address)``


Claim Amount
^^^^^^^^^^^^

**uint claimAmount**

Ammount that the ``claimer`` has agreed to pay for the call. Retrieved with the
with the ``claimAmount`` function.

* **Solidity Function Signature:** ``claimAmount() returns (uint)``


Claim Deposit
^^^^^^^^^^^^^

**uint claimerDeposit**

Ammount that the ``claimer`` put down as a deposit. Retrieved with the
with the ``claimerDeposit`` function.

* **Solidity Function Signature:** ``claimerDeposit() returns (uint)``


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


Execute
^^^^^^^

Triggers the execution of the call.  This can only be done during the window
between the ``targetBlock`` through the end of the ``gracePeriod``.  If the
call has been claimed, then only the claiming address can execute the call
during the first 16 blocks.  If the claming address does not execute the call
during this time, anyone who subsequently executes the call will receive their
deposit.

* **Solidity Function Signature:** ``execute() public``
