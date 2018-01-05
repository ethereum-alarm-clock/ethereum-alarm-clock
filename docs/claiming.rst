Claiming
========

.. contents:: :local:

.. class:: TransactionRequest
    :noindex:

The Problem
-----------

The claiming mechanism solves a very important problem contained within the 
incentive scheme of the EAC. It's best to provide an example first then go into 
the specifics of the solution later.

Consider a situation where there are two people, Alice and Bob, competing to
execute the same request. The request will issue a payment of 100 wei to whomever
executes it.

Suppose that Alice and Bob both send their execution transactions at
approximately the same time, but out of luck, Alice's transaction is included
before Bob's.

Alice will receive the 100 wei payment, while Bob will receive no payment as
well as having paid the gas costs for his execution transaction that was
rejected.  Suppose that the gas cost Bob has now incurred is 25 wei.

In this situation we could assume that Alice and Bob have a roughly 50% chance
of successfully executing any given transaction request, but since 50% of their
attempts end up costing them money, their overall profits are being reduced by
each failed attempt.

In this model, their expected payout is 75 wei for every two transaction
requests they try to execute.

Now suppose that we add more competition via three additional people attempting
to execute each transaction.  Now Bob and Alice will only end up executing an
average of 1 out of every 5 transaction requests, with the other 4 costing them
25 wei each.  Now the result is that nobody is making a profit because the cost 
of the failed transactions cancel out any profit they are making.


The Solution
------------

The claiming process is the current solution to this issue.

Prior to the execution window there is a section of time referred to as the
claim window during which the request may be claimed by a single party for
execution.  An essiential part of claiming is that the claimer must put down 
a claim deposit in order to attain the rights to execute the request.

When a request has been claimed, the claimer is granted exclusive rights to
execute the request during a window of blocks at the beginning of the execution
window.

Whomever ends up executing the request receives the claim deposit as part of
their payment.  This means that if the claimer fulfills their commitment to
execute the request their deposit is returned to them intact.  Otherwise, if
someone else executes the request then they will receive the deposit as an
additional reward.


Claim Deposit
-------------

In order to claim a request you must put down a deposit.  This deposit amount
is specified by the scheduler of the transaction. The account claiming 
the transaction request must send at least the ``claimDeposit`` amount
when they attempt to claim an execution.

The ``claimDeposit`` is returned to the claiming account when they 
execute the transaction request or when the call is cancelled. However,
if the account that claims the call later fails to execute then they will 
lose their claim deposit to whoever executes instead.


How claiming effects payment
----------------------------

A claimed request does not pay the same as an unclaimed request.  The earlier the
request is claimed, the less it will pay, and conversely, the later the request is
claimed, the more it pays.

This is a linear transition from getting paid 0% of the total payment if the
request is claimed at the earliest possible time up to 100% of the total payment
at the very end of the claim window.  This multiplier is referred to as the
*payment modifier*.  Refer to the code block pasted below to see how the smart 
contract calculates the multiplier. This examples is taken from lines 71 - 79 
of `RequestScheduleLib.sol`.


.. code-block:: solidity

    function computePaymentModifier(ExecutionWindow storage self) 
        internal view returns (uint8)
    {        
        uint paymentModifier = (getNow(self).sub(firstClaimBlock(self)))
                                .mul(100).div(self.claimWindowSize); 
        assert(paymentModifier <= 100); 

        return uint8(paymentModifier);
    }


It is important to note that the *payment modifier* does not apply to gas
reimbursements which are always paid in full.  No matter when a call is
claimed, or how it is executed, it will **always** provide a full gas
reimbursement.  

.. note:: 
    In the past, this was not always the case since the EAC used a slightly different 
    scheme to calculate an anchor gas price.  In version 0.9.0 
    the anchor gas price was removed in favor of forcing the scheduler of the transaction 
    to explicitly specify an **exact** gas price.  So the gas to execute a transaction is
    always reimbursed exactly to the executor of the transaction.

For clarification of the payment modifier let's consider an example.
Assume that a transaction request has a ``payment`` set to 2000 wei, a
``claimWindowSize`` of 255 blocks, a ``freezePeriod`` of 10 blocks, and a
``windowStart`` set at block 500.  The first claimable block is calculated by
subtracting the ``claimWindowSize`` and the ``freezePeriod`` from the ``windowStart``
like so:

``first_claim_block = 500 - 255 - 10 = 235``

In this case, the request would have a payment of 0 at block 235.  

``(235 - 235) * 100 // 255 = 0``

At block 245 it would pay 60 wei or 3% of the total payment.

``(245 - 235) * 100 // 255 = 3``

At block 489 it would pay 1980 wei or 99% of the total payment.

``(489 - 235) * 100 // 255 = 99``

Gas Costs
---------

The gas costs for claim transactions are *not* reimbursed.  They are considered
the cost of doing business and should be taken into consideration when claiming
a request.  If the request is claimed sufficiently early in the claim window it
is possible that the ``payment`` will not fully offset the transaction costs of
claiming the request.  EAC clients should take precaution that they do not claim 
transaction requests without estimating whether they will be profitable first. 
