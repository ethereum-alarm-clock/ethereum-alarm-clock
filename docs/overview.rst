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

1. Schedule the function call with the service.
2. Register any call data that will be required to make the function call
   (optional for functions that have no arguments).


Call Scheduling
^^^^^^^^^^^^^^^

Function calls can be scheduled for any block at least 40 blocks *(~10 minutes)*
in the future.  Scheduling is done by providing the Alarm service with the
following information:

1. Contract address the call should be executed on.
2. ABI signature of the function that should be called.
3. Target block number that the call should be executed on.

Optionally, these additional pieces of information can be supplied.

* Suggested gas amount that should be provided to the function.  **default: 0
  to indicate no suggestion**
* Number of blocks after the target block during which it still ok to execute
  the call.  (between 64 - 255 blocks) **default: 255**
* Payment amount in wei that will be paid to the executor of the call.
* Fee amount in wei that will be paid to the creator of the Alarm service.

The scheduling transaction must also include enough ether to pay for the gas
costs of the call as well as the payment and fee values.

Once scheduled, the call waits to be picked up and executed at the desired block.


Registering Call Data
^^^^^^^^^^^^^^^^^^^^^

The Alarm service is not aware of the function ABI for the calls it executes.
Instead, it uses the function ABI signature and raw call data to execute the
function call.

To do this, any data that needs to be used in the call must be registered prior
to scheduling the call.  Functions which do not have any arguments can skip
this step.


Execution of scheduled calls
----------------------------

Scheduled function calls can ultimately be executed by anyone who wishes to
initiate the transaction.  This will likely be an automated process that
monitors for upcoming scheduled calls and executes them at the appropriate
block.


Usage Fees
^^^^^^^^^^

In addition to the gas costs, schedulers are also encouraged to pay the call
executor as well as the creator of the service for their effort.  This value
can be specified by the scheduler, meaning that you may choose to offer any
amount (including zero).

The scheduling function uses the following defaults if specific values are not
provided.

* Payment to the executor: **1 ether**
* Payment to the service creator: **100 finney**

Guarantees
----------

Will the call happen?
^^^^^^^^^^^^^^^^^^^^^

There are no guarantees that your function will be called.  This is not a
shortcoming of the service, but rather a fundamental limitation of the ethereum
network.  Nobody is capable of forcing a transaction to be included in a
specific block.

The design of this service is meant to provide the proper motivation for calls
to be executed, but it is entirely possible that certain calls will be missed
due to unforseen circumstances.  Providing a higher Payment amount is a
potential way to get your scheduled call handled at a higher priority as it
will be more profitable to execute.


Will I get paid for executing a call?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are diligent about how you go about executing scheduled calls then
executing scheduled calls is guaranteed to be profitable.  See the section on
executing calls for more information.
