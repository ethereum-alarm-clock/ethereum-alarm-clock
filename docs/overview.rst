Overview
========

The Ethereum Alarm service is a contract on the ethereum network that
facilitates scheduling of function calls for a specified block in the future.
It is designed to require zero trust between any of the users of the
service, as well as providing no special access to any party (including the
author of the service)


Scheduling Function Calls
-------------------------

Contracts, or individuals can schedule a function calls with the Alarm
service by doing the following.

1. Schedule the function call with the service, providing basic information
   such as what function to call and when it should be called.
2. Register any call data that will be required to make the function call
   (optional for functions that have no arguments).


Call Scheduling
^^^^^^^^^^^^^^^

Function calls can be scheduled for any block at least 10 blocks *(~3 minutes)*
in the future.  Scheduling is done by calling the ``scheduleCall`` function on
the scheduling contract.  This function has a wide variety of call signatures
that allow the scheduler to specify any of the following information.

#. Contract address the call should be executed on.
#. ABI signature of the function that should be called.
#. Bytes of call data that should be passed along.
#. Value in Ether to be sent with the call.
#. Target block number that the call should be executed on.
#. Number of blocks after the target block during which it still ok to execute
   the call.  (between 64 - 255 blocks)
#. Required gas that must be provided with the executing transaction.
#. Stack depth check.
#. Payment amount in wei that will be paid to the executor of the call.
#. Donation amount in wei that will be paid to the creator of the Alarm
   service.

The scheduling transaction must also include enough ether to pay for the gas
costs of the call as well as the payment and fee values.


Execution of scheduled calls
----------------------------

Scheduled function calls can be executed by anyone who wishes to initiate the
transaction who in turn is paid whatever amount was specified as the payment
value for the call.


Cost
^^^^

In addition to the gas costs, schedulers are also encouraged to include a payment
amount for the executor of the call.  This value can be specified by the
scheduler, meaning that you may choose to offer any amount for the execution of
your function.

The scheduling function uses the following defaults if specific values are not
provided.

* Payment to the executor: **market value**
* Payment to the service creator: **1/100th market value**

The market value is determined by the market history of scheduled calls.


Guarantees
----------

Will the call happen?
^^^^^^^^^^^^^^^^^^^^^

There are no guarantees that your function will be called.  This is not a
shortcoming of the service, but rather a fundamental limitation of the ethereum
network.  Nobody is capable of forcing a transaction to be included in a
specific block.

The Alarm service has been designed such that it **should** become more
reliable as more people use it.

However, it is entirely possible that certain calls will be missed
due to unforseen circumstances.  Providing a higher Payment amount is a
potential way to get your scheduled call handled at a higher priority as it
will be more profitable to execute.


Will I get paid for executing a call?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are diligent about how you go about executing scheduled calls then
executing scheduled calls is guaranteed to be profitable.  See the section on
executing calls for more information.
