Introduction
============

.. contents:: :local:


What problem does this solve
----------------------------

The simplest way to explain the utility of the Alarm service is to explain the
problem it solves.

First, you need to understand the difference between private key based accounts
and contract accounts.  There are two types of accounts on the Ethereum
blockchain.

1. Accounts that have a private key.
2. Contracts *(which do not have a private key)*

Private key accounts are the accounts that humans operate, where as contract
accounts are deployed pieces of code capable of executing some computer
program.  Contract accounts cannot however trigger their own code execution.

All code execution in the Ethreum Virtual Machine, or EVM must be triggered by
a private key based account.  This is done by sending a transaction, which may
do something simple like transfering ether, or it may do something more complex
like calling a function on a contract account.

The second part of the problem is that when you send a transaction it is
executed as soon as it is included in a block.  The Ethereum protocol does not
provide any way to create a transaction to be executed at a later time.

This leads us to the problem that the Alarm service solves.  With the
functionality provided by this service, transactions can be securely scheduled
to be executed at a later time.


How transactions are executed
-----------------------------

When a transaction is scheduled a new smart contract is created that holds all
of the information needed to execute the transaction.  It may be useful to
think of this as an order on an exchange.  When called during the specified
execution window, this contract will send the transaction as specified and then
pay the account that triggered the execution.

These contracts are referred to as :class:`TransactionRequest` contracts and
are written to provide strong guarantees of correctness to both parties.

The creator of the :class:`TransactionRequest` contract can know that their
transaction will only be sent during the window they specified and that the
transaction parameters will be sent exactly as specified.

Similarly, the account that executes the :class:`TransactionRequest` contract
can know that no matter what occurs during the execution of the transaction
that they will receive full gas reimbursement as well as their payment for
execution.


Execution guarantees
--------------------

You may have noted at this point that this service relies on external parties
to initiate the execution of these transactions.  This means that it is
possible that your transaction will not be executed at all.  

In an ideal situation, there is a sufficient volume of scheduled transactions
that operating a server to execute these transactions is a profitable endeavor.
The reality is that I operate between 3-5 execution servers dedicated filling
this role until there is sufficient volume that I am confident I can turn those
servers off or until it is no longer feasible for me to continue paying their
costs.


How scheduling transactions works
---------------------------------

A transaction is scheduled by providing some or all of the following
information.

* Details about the transaction itself such as which address the transaction
  should be sent to, or how much ether should be sent with the transaction.
* Details about when the transaction can be executed.  This includes things
  like the window of time or blocks during which this transaction can be
  executed.
* Ether to pay for the transaction gas costs as well as the payment that will
  be paid to the account that triggers the transaction.

Scheduling is done by calling a :class:`Scheduler` contract which handles
creation of the individual :class:`TransactionRequest` contract.
