Terminology
===========

Definitions for various terms that are used regularly to describe parts of the
Alarm service.

General
-------

.. glossary::

    Ethereum Alarm Clock
    Alarm
    Alarm Service
        Generic terms for the service as a whole.

    Scheduler Contract
        The solidity contract responsible for scheduling a function call.

    Call Contract
        The solidity contract that is deployed for each scheduled call.  This
        contract handles execution of the call, registration of call data, gas
        reimbursment, and payment and fee dispursment.

    Scheduled Call
        A contract function call that has been registered with the Alarm
        service to be executed at a specified time in the future (currently
        denoted by a block number).


Calls and Call Scheduling
-------------------------


.. glossary::

    Scheduler
        The account which scheduled the function call.

    Executor
        The account which initiates the transaction which executes a scheduled
        function call.

    Target Block
        The first block number that a scheduled call can be called.

    Grace Period
        The number of blocks after the **target block** that a scheduled call
        can be be called.

    Freeze Window
        The 10 blocks directly preceeding the target block for a call

    Claim Window
        The 255 block window prior to the Freeze Window during which the call
        may be claimed for exclusive rights to execution during the first 16
        blocks of the call window.

    Call Window
        Used to refer to either the full window of blocks during which a
        scheduled call can be executed, or a portion of this window that has
        been designated to a specific caller.

    Payment
        The ethereum amount that is paid to the executor of the scheduled call.

    Fee
        The ethereum amount that is paid to the creator of the Alarm service.

    Anchor Gas Price
        The gas price that was used when scheduling the scheduled call.

    Gas Price Scalar
        A number ranging from 0 - 2 that is derived from the difference between
        the gas price of the executing transaction and the **anchor gas
        grice**.  This number equals 1 when the two numbers are equal. It
        approaches 2 as the executing gas grice drops below the anchor gas
        price.  It approaches zero as the executing gas price rises above the
        anchor gas price.  This multiplier is applied to the payment and fee
        values, intending to motivate the executor to use a reasonable gas
        price.
