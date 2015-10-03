Overview
========

The Ethereum Alarm service is a contract on the ethereum network that
facilitates scheduling of function calls for a specified block in the future.
It is designed to require little or no trust between any of the users of the
service, as well as providing no special access to the creator of the
contract.

Scheduling Function Calls
-------------------------

When a contract, or individual wants to schedule a function call with the Alarm
service it will perform the following steps.

1. Ensure that the account that is scheduling the call has a sufficient balance
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
funds to pay for the execution of the scheduled call, it will be skipped.

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
5. Number of blocks after the target block during which it still ok to execute
   the call.
6. A nonce to allow differentiation between identical calls that are scheduled
   for the same block.

Once scheduled, the call waits to be picked up and executed at the desired block.


Execution of scheduled calls
----------------------------

Scheduled function calls can ultimately be executed by anyone who wishes to
initiate the transaction.  This will likely be an automated process that
monitors for upcoming scheduled calls and executes them at the appropriate
block.


Usage Fees
^^^^^^^^^^

A scheduled function call costs approximately 102% of the total gas expenditure
for the transaction in which it was executed.

The additional 2% is split evenly between paying the account which executed the
function call and the creator of the Alarm service for the many many hours
spent creating it.

Guarantees
----------

Will the call happen?
^^^^^^^^^^^^^^^^^^^^^

There are no guarantees that your function will be called.  The design of this
service is meant to provide the proper motivation for calls to be executed, but
it is entirely possible that certain calls will be missed due to unforseen
circumstances.

Will I get paid for executing a call?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are diligent about how you go about executing scheduled calls, there
should be a near 0% chance that you will not be reimbursed for your gas costs.
See the section on executing calls for more information on how to protect
yourself.
