Claiming
========

.. contents:: :local:

.. class:: TransactionRequest

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

I
