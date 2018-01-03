Quickstart
==========

.. contents:: :local:


Introduction
------------

This guide is inteded for smart contract developers that may want to use the EAC services 
from within their own applications. Since all the functionality of the Alarm Clock 
is built into the Ethereum chain via smart contracts, it can be accessed from other 
contracts. This makes it useful as a foundational tool to design and implement more 
complex utilities that depend on future transactions. For this guide we will be using 
the Solidity language. If you are unfamiliar with Solidity we recommend you familiarize 
yourself with its `documentation`_ first. 


Scheduling your first transaction
---------------------------------

The first step is to establish how we will interact with the EAC service's
:class:`Scheduler` contract.  We can use the Scheduler Interface to accomplish this. 
The Scheduler interface contract contains some logic that is shared between both the 
Block Scheduler and the Timestamp Scheduler.  The function that we are interested in is the 
`schedule()` function.  See the signature of this function below:


.. code-block:: solidity 

    function schedule(address   _toAddress,
                      bytes     _callData,
                      uint[7]   _uintArgs)
        doReset
        public payable returns (address);


``SchedulerInterface.sol`` is an abstract contract that exposes the API for the Schedulers
including the ``schedule()`` function that we will use in the contract we write. 

function ``schedule`` which will
return the address of the newly created :class:`TransactionRequest` contract.  We will import this 
contract into the contract we write so to ensure that our contract will be 
compliant with the official API of the EAC.

Now lets write a simple contract that can use the scheduling service.


.. literalinclude:: ../contracts/_examples/DelayedPayment.sol 
    :language: solidity 


The contract above is designed to lock away whatever ether it is given for
``numBlocks`` blocks.  In its constructor, it makes a call to the
``schedule`` method on the ``scheduler`` contract.  We would pass in 
the address of the scheduler we would want to interact with as the first 
parameter of the constructor.  For instance, if we wanted to use the Block
Scheduler that is deployed on the Ropsten test net we would use address 
``0x96363aea9265913afb8a833ba6185a62f089bcef``.  

The function only takes 3 parameters at deployment, with the 7 parameters 
being into the schedule function being set by the developer of the smart 
contract.  The schedule function takes 7 arguments, each of which we will go 
over in order.


* ``address toAddress``: The ``address`` which the transaction will be sent to.
* ``bytes callData``: The ``bytes`` that will be used as the data for the transaction.
* ``uint callGas``: The amount of gas that will be sent with the transaction.
* ``uint callValue``: The amount of ether (in wei) that will be sent with the transaction.
* ``uint8 windowSize``: The number of blocks after ``windowSize`` during which the transaction will still be executable.
* ``uint windowStart``: The first block number that the transaction will be executable.
* ``uint gasPrice``: The gas price which must be sent by the executing party to execute the transaction.
* ``uint donation``: The donation amount included in the transaction.
* ``uint payment``: The payment included in the transaction.


Let's look at the other function on this contract.  For those unfamiliar with solidity,
the function without a name is known as the fallback function.  The fallback 
function is what triggers if no method is found on the contract that matches 
the sent data, or if data is not included.  Usually, sending a simple value transfer function 
will trigger the fallback function.  In this case, we explicitly pass an empty string 
as the ``callData`` variable so that the scheduled transaction will trigger this 
function when it is executed.

When the fallback function is executed, if the contract has a balance (which it does 
since we sent it 2 ether on deployment) it will route the call into the ``payout()`` function.
The ``payout()`` function will check the current block number and check if it is not 
below the ``lockedUntil`` time or else it reverts the transaction.  After it 
checks that the current block number is greater than or equal to the lockedUntil 
variable, the function will transfer the entrie balance of the contract to the 
specified recipient. 

As can be seen, this will make it so that a payment is scheduled for a future 
date but won't actually be sent until that date.  This example uses a simple 
payment, but the EAC will work with arbritrary logic.  As the logic for a scheduled 
transaction increases, be sure to increase the required ``callGas`` in accordance.
Right now, the gas limit for a transaction is somewhere in the ballpark of 8,000,000 
so there's plenty of wiggle room for experimentation.

.. _documentation: https://solidity.readthedocs.io/en/develop/