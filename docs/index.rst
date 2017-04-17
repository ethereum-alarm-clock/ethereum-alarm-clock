.. Ethereum Alarm Clock documentation master file, created by
   sphinx-quickstart on Sun Sep 13 11:14:18 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Ethereum Alarm Clock's documentation!
================================================

The Ethereum Alarm Clock is a service that allows scheduling transactions to be
executed at a later time on the ethereum blockchain.  This is accomplished by
specifying all of the details for the transaction you wish to send, as well as
providing up-front payment for gas costs, allowing your transaction to be
executed for you at a later time.

The service is completely trustless, meaning that the entire service operates
as smart contracts on the Ethereum blockchain, with no priviledged access given
to any party.

The code for this service is open source under the MIT license and can be
viewed on the `github repository`_.  Each release of the alarm service includes
details on verifying the contract source code.

For a more complete explanation of what this service does check out the
:doc:`./introduction`.

If you are a smart contract developer and would like to start scheduling
transactions now then check out the :doc:`./quickstart`.

If you are looking to build a lower level integration with the service then our
`./TODO` is a good place to start.


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
   cli
   changelog


.. _github repository: https://github.com/pipermerriam/ethereum-alarm-clock
