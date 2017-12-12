Quickstart
==========

.. contents:: :local:


Scheduling your first transaction
---------------------------------

The first step is to establish how we will interact with the Alarm service's
:class:`Scheduler` contract.  Lets create an abstract contract to accomplish
this.


.. code-block:: solidity

    contract SchedulerInterface {
        //
        // params:
        // - uintArgs[0] callGas
        // - uintArgs[1] callValue
        // - uintArgs[2] windowStart
        // - uint8 windowSize
        // - bytes callData
        // - address toAddress
        //
        function scheduleTransaction(address toAddress,
                                     bytes callData,
                                     uint8 windowSize,
                                     uint[3] uintArgs) public returns (address);
    }


This abstract contract exposes the function ``scheduleTransaction`` which will
return the address of the newly created :class:`TransactionRequest` contract.

Now lets write a simple contract that can use the scheduling service.


.. code-block:: solidity

    contract DelayedPayment {
        SchedulerInterface constant scheduler = SchedulerInterface(0xTODO);

        uint lockedUntil;
        address recipient;

        function DelayedPayment(address _recipient, uint numBlocks) {
            // set the time that the funds are locked up
            lockedUntil = block.number + numBlocks;
            recipient = _recipient;

            uint[3] memory uintArgs = [
                200000,      // the amount of gas that will be sent with the txn.
                0,           // the amount of ether (in wei) that will be sent with the txn
                lockedUntil, // the first block number on which the transaction can be executed.
            ];
            scheduler.scheduleTransaction.value(2 ether)(
                address(this),  // The address that the transaction will be sent to.
                "",             // The call data that will be sent with the transaction.
                255,            // The number of blocks this will be executable.
                uintArgs,       // The tree args defined above
            )
        }

        function() {
            if (this.balance > 0) {
                payout();
            }
        }

        function payout() public returns (bool) {
            if (now < lockedUntil) return false;

            return recipient.call.value(this.balance)();
        }
    }


The contract above is designed to lock away whatever ether it is given for
``numBlocks`` blocks.  In its constructor, it makes a call to the
``scheduleTransaction`` method on the ``scheduler`` contract.  The function
takes a total of 6 parameters, 3 of which are passed in as an array.  Lets
briefly go over what each of these parameters are.


.. method:: scheduleTransaction(address toAddress,
                                bytes callData,
                                uint8 windowSize,
                                [uint callGas, uint callValue, uint windowStart])

* ``address toAddress``: The ``address`` which the transaction will be sent to.
* ``bytes callData``: The ``bytes`` that will be used as the data for the transaction.
* ``uint callGas``: The amount of gas that will be sent with the transaction.
* ``uint callValue``: The amount of ether (in wei) that will be sent with the transaction.
* ``uint windowStart``: The first block number that the transaction will be executable.
* ``uint8 windowSize``: The number of blocks after ``windowSize`` during which
  the transaction will still be executable.


TODO: more
