.. Ethereum Alarm Clock documentation master file, created by
   sphinx-quickstart on Sun Sep 13 11:14:18 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Ethereum Alarm Clock's documentation!
================================================

The Ethereum Alarm Clock (EAC for short) is a collection of smart contracts on 
Ethereum that aims to allow for the scheduling of transactions to be executed 
at a later time. It is a "ÐApp" in the truest sense of the word since it has the 
qualities of being trustless, censorship resistant and decentralized. No matter 
who you are or where you are located, there is no way for anyone to stop you from 
scheduling a transaction or running an execution client. There is no priviledged access 
given to any party, not even to the developers =)

On a high level it works by some users scheduling transactions and providing the execution 
details and payments up front, while other users run execution clients that 
scan the blockchain looking for upcoming transactions. When the execution 
clients find upcoming transactions they keep track of them and compete 
to claim and execute them -- whoever gets the rights to the execution gets 
paid the exeuction reward.

The code for this service is open source under the MIT license and can be
viewed on the `github repository`_.  Each release of the alarm service includes
details on verifying the contract source code.

For a more complete explanation of what this service does check out the
:doc:`./introduction`.

If you are a smart contract developer and would like to see an example for 
how you can use the EAC smart contracts from your own code see :doc:`./quickstart`.

If you are looking to acquire a deeper understanding of the architecture then
it is recommnended you skim the documentation in full. It is recommnended to 
also view the source code.


Contents:

.. toctree::

   introduction
   quickstart
   architecture
   transaction_request
   claiming
   execution
   request_factory
   request_tracker
   scheduler
   changelog


.. _github repository: https://github.com/pipermerriam/ethereum-alarm-clock
