Account Managment
=================

The *scheduler pays* system requires that payment for scheduled calls be
provided prior to the execution of the call, so that the sender of the
executing transaction can immediately be reimbursed for the gas costs.

The account and associated funds for each ethereum address are used to pay for
the calls scheduled by that address.  Inturn, each ethereum address may
withdraw or deposit funds in its account at any time with no restrictions.

It is also possible to deposit funds in the account of another address.  You
cannot however withdraw funds from any address other than your own.

Checking account balance
------------------------

Your account balance can be checked by accessing the public mapping of accounts
to balances.

* **Soldity Function Signature:** ``accountBalances(address accountAddress) returns (uint)``
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

Here is how you would do this from the geth javascript console.

.. code-block::

    > eth.sendTransaction({from:"0x...", to:"0x...", value:100})
    "0x9fc76417374aa880d4449a1f7f31ec597f00b1f6f3dd2d66f4c9c6c445836d8b"

The above would deposit 100 wei in the account of whatever address you used for
the ``from`` value in the transaction.
