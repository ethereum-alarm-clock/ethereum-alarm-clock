Claiming
========

.. contents:: :local:

.. class:: TransactionRequest
    :noindex:

The Problem
-----------

To understand the claiming mechanism it is important to understand the problem
it solves.

Consider a situation where there are two people Alice and Bob competing to
execute the same request that will issue a payment of 100 wei to whomever
executes it.

Suppose that Alice and Bob both send their execution transactions at
approximately the same time, but out of luck, Alice's transaction is included
before Bob's.

Alice will receive the 100 wei payment, while Bob will receive no payment as
well as having paid the gas costs for his execution transaction that was
rejected.  Suppose that the gas cost Bob has now incurred are 25 wei.

In this situation we could assume that Alice and bob have a roughly 50% chance
of successfully executing any given transaction request, but since 50% of their
attempts end up costing them money, their overall profits are being reduced by
each failed attempt.

In this model, their expected payout is 75 wei for every two transaction
requests they try to execute.

Now suppose that we add more competition via three additional people attempting
to execute each transaction.  Now Bob and Alice will only end up executing an
average of 1 out of every 5 transaction requests, with the other 4 costing them
25 wei each.  Now nobody is making a profit because the cost of the failed
transactions now cancels out any profit they are making.


The Solution
------------

The claiming process is the current solution to this issue.

Prior to the execution window there is a section of time referred to as the
claim window during which the request may be claimed by a single party for
execution.  Part of claiming includes putting down a deposit.

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
is equal to twice the ``payment`` amount associated with this request.

The deposit is returned during execution, or when the call is cancelled.


How claiming effects payment
----------------------------

A claimed request does not pay the same as an unclaimed request.  The earlier the
request is claimed, the less it will pay, and conversely, the later the request is
claimed, the more it pays.

This is a linear transition from getting paid 0% of the total payment if the
request is claimed at the earliest possible time up to 100% of the total payment
at the very end of the claim window.  This multiplier is referred to as the
*payment modifier*.

It is important to note that the *payment modifier* does not apply to gas
reimbursements which are always paid in full.  No matter when a call is
claimed, or how it is executed, it will **always** provide a full gas
reimbursement.  The only case where this may end up not being true is in cases
where the gas price has changed drastically since the time the request was
scheduled and the contract's endowment is now sufficiently low that it is not
longer funded with sufficient ether to cover these costs.

For example, if the request has a ``payment`` of 2000 wei, a
``claimWindowSize`` of 255 blocks, a ``freezePeriod`` of 10 blocks, and a
``windowStart`` set at block 500.  In this case, the request would have a
payment of 0 at block 235.  At block 235 it would provide a payment of 20 wei.
At block 245 it would pay 220 wei or 11% of the total payment.  At block 489 it
would pay 2000 wei or 100% of the total payment.


Gas Costs
---------

The gas costs for claim transactions are *not* reimbursed.  They are considered
the cost of doing business and should be taken into consideration when claiming
a request.  If the request is claimed sufficiently early in the claim window it
is possible that the ``payment`` will not fully offset the transaction costs of
claiming the request.
