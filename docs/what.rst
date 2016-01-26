What is it?
===========

Alarm is a service that operates on the Ethereum world computer.

Within the network there are two types of accounts.

* Contracts: Controlled by a piece of code that has been deployed to the
  Ethereum network.
* Private Key: Accounts that are controlled by a private key which is used to
  sign transaction.

The only difference between the capabilities of these two types of accounts is
that only Private Key based accounts can initiate the execution of code which
is done by sending a signed transaction into the Ethereum network.

A common requirement for software systems is execution of code at a specified
time in the future.  An example of one such mechanism is the crontab on unix
based systems.

The Alarm service serves a similar purpose to Contracts on Ethereum.  Since
contracts are unable to initiate transactions themselves, the Alarm service
sets up a marketplace that allows the operator of a private key based account
to claim a reward in exchange for initiating the required transaction.
