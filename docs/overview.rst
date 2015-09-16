Overview
========

The Ethereum Alarm service is a DApp or contract on the ethereum network.  It
is designed to require little or no trust between any of the users of the
service, as well as providing no special access to the creators of the
contract.

Scheduling Function Calls
-------------------------

When a contract, or individual wants to schedule a function call with the Alarm
Service it will perform the following steps.

1. Ensure that the account that will schedule the call has a sufficient balance
   to pay for the scheduled call.
2. Register any call data that will be required to make the function call.
3. Schedule the function call with the service.

Account Balance
^^^^^^^^^^^^^^^

The Alarm service operates under a *scheduler pays* model meaning that the
address which schedules the function call is required to pay for it. When a
call is executed, the initial gas cost is paid for by the ethereum address that
sends the executing transaction.  This address needs to be reimbursed this gas
cost plus a small fee.  The Alarm service requires this payment up front in the
form of an account balance.

The Alarm service maintains accounts for each address on the network.  These
accounts can have ether deposited and withdrawn at any time.  However, at the
time the call is executed, if the scheduler's account does not have enough
funds to pay for 102% of the maximum possible transaction cost for the block
the call is executed on, the call will be skipped.

Registering Call Data
^^^^^^^^^^^^^^^^^^^^^

The Alarm service is not aware of the function ABI for the calls it executes.
Instead, it uses the function ABI signature and raw call data to execute the
function call.

To do this, any data that needs to be used in the call must be registered prior
to scheduling the call.  Call data only needs to be registered once, and can be
re-used for subsequent function calls.

Call Scheduling
^^^^^^^^^^^^^^^

Function calls can be scheduled for any block at least 40 blocks *(~10 minutes)*
in the future.  Scheduling is done by providing the Alarm service with the
following information:

1. Contract address the call should be executed on.
2. ABI signature of the function that should be called.
3. SHA3 hash of the call data that should be included in the function call.
4. Target block number that the call should be executed on.

Once scheduled, the call should be picked up and executed at the desired block.


Execution of scheduled calls
----------------------------

Scheduled function calls can ultimately be executed by anyone who wishes to
initiate the transaction.  This will likely be an automated process that
monitors for upcoming scheduled calls and executes them at the appropriate
block.

Usage Fees
^^^^^^^^^^

A scheduled function call costs 102% of the total gas expenditure for the
transaction in which it was executed.

In return for executing the function call at the appropriate block, the sender
of the transaction is reimbursed the 101% of gas cost of the transaction
(earning them 1% of the transaction gas cost).

In addition to the 1% sent to the sender of the transaction, an additional 1%
fee is sent to the *owner* of the contract.  This is payment to the author of
this service for the many many hours spent creating it.

Guarantees
----------

Will the call happen?
^^^^^^^^^^^^^^^^^^^^^

There are no guarantees that your function will be called.  The design of this
service is meant to provide the proper motivation for all involved parties, but
it is entirely possible that certain calls will be missed due to unforseen
circumstances.

Will I get paid for executing a call?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are diligent about how you go about executing scheduled calls, there
should be a near 0% chance that you will not be reimbursed for your gas costs.
See the section on executing calls for more information on how to protect
yourself.
