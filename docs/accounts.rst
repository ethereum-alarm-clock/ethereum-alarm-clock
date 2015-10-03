Account Managment
=================

The *scheduler pays* system requires that payment for scheduled calls be
provided prior to the execution of the call, so that the sender of the
executing transaction can immediately be reimbursed for the gas costs.

The account and associated funds are used to pay for any calls scheduled by
that address.  Inturn, each ethereum address may withdraw or deposit funds in
its account at any time with no restrictions.

It is also possible to deposit funds in the account of another address.  You
cannot however withdraw funds from any address other than your own.

Checking account balance
------------------------

Your account balance can be checked by accessing the public mapping of accounts
to balances.

* **Solidity Function Signature:** ``accountBalances(address accountAddress) returns (uint)``
* **ABI Signature:** ``0x6ff96d17``

Calling this function will return the balance in wei for the provided address.

Depositing funds
----------------

Depositing funds can be done one of a few ways.  

By sending ether
^^^^^^^^^^^^^^^^

The simplest way to add funds to your account is to just send the ether to the
address of the alarm service.  Any funds sent to the alarm service are added to
the account balance of the sender.

.. warning::

    Contracts cannot add funds to their accounts this way using the ``send``
    function on addresses.  This is due to solidity's protection against
    unbounded gas use in contract fallback functions.  See below for how
    contracts can add their own funds.

Here is how you would do this from the geth javascript console.

.. code-block::

    > eth.sendTransaction({from:"0x...", to:"0x...", value:100})
    "0x9fc76417374aa880d4449a1f7f31ec597f00b1f6f3dd2d66f4c9c6c445836d8b"

The above would deposit 100 wei in the account of whatever address you used for
the ``from`` value in the transaction.

By using the deposit function
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Funds can also be deposited in a specific account by calling the ``deposit``
function and sending the desired deposit value with the transaction.

* **Solidity Function Signature:** ``deposit(address accountAddress)``
* **ABI Signature:** ``0xf340fa01``


Sending from a contract
^^^^^^^^^^^^^^^^^^^^^^^

Contracts can deposit funds through these mechanisms as well.

.. code-block::

    contract DepositsFunds {
        function doTheDeposit(address alarmAddress, uint value) public {
            alarmAddress.call.value(value)();
        }
    }

Or, if you would like your contract to deposit funds in the account of another
address.

.. code-block::

    contract DepositsFunds {
        function doTheDeposit(address alarmAddress, uint value, address accountAddress) public {
            alarmAddress.call.value(value)(bytes4(sha3("deposit(address)")), accountAddress);
        }
    }

.. note::

    It should be pointed out that you cannot deposit funds by calling
    ``alarmAddress.send(value)``.  By default in solidity, this transaction is sent
    with only enough gas to execute the funds transfer, and the fallback function
    on the Alarm service requires a bit more gas so that it can record the increase
    in account balance.


Withdrawing funds
-----------------

Withdrawing funds is restricted to the address they are associated with.  This
is done by calling the ``withdraw`` function on the Alarm service.

* **Solidity Function Signature:** ``withdraw(uint value)``
* **ABI Signature:** ``2e1a7d4d``

If the account has a balance sufficient to fulfill the request, the amount specified
specified in wei will be transferred to ``msg.sender``.
