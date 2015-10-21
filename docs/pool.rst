Caller Pool
===========

The Alarm service maintains a pool of bonded callers who are responsible for
executing scheduled calls.  By joining the caller pool, an account is
committing to executing scheduled calls in a reliable and consistent manner.
Any caller who reliably executes the calls which are allocated to them will
make a consistent profit from doing so, while callers who don't get removed
from the pool and forfeit some or all of their bond.


Caller Bonding
--------------

In order to execute scheduled calls, callers put up a small amount of ether up
front.  This bond, is held for the duration that a caller remains in the caller
pool.


Minimum Bond
^^^^^^^^^^^^

The bond amount is set as the maximum allowed transaction cost for a given
block.  This value can be retrieved with the ``getMinimumBond`` function.

* **Solidity Function Signature:** ``getMinimumBond() returns (uint)``
* **ABI Signature:** ``0x23306ed6``

This value can change from block to block depending on the gas price and gas
limit.

Depositing your bond
^^^^^^^^^^^^^^^^^^^^

Use the ``depositBond`` function on the Caller Pool to deposit ether towards
your bond.

* **Solidity Function Signature:** ``depositBond()``
* **ABI Signature:** ``0x741b3c39``

Checking bond balance
^^^^^^^^^^^^^^^^^^^^^

Use the ``getBondBalance`` function to check the bond balance of an account.

* **Solidity Function Signature:** ``getBondBalance(address) returns (uint)``
* **ABI Signature:** ``0x33613cbe``

Or to just check the balance of the sender of the transaction.

* **Solidity Function Signature:** ``getBondBalance(address) returns (uint)``
* **ABI Signature:** ``0x3cbfed74``


Withdrawing your bond
^^^^^^^^^^^^^^^^^^^^^

Use the ``withdrawBond`` function on the Caller Pool to withdraw the bond
ether.

* **Solidity Function Signature:** ``withdrawBond()``
* **ABI Signature:** ``0xc3daab96``

If you are currently in a call pool, either active or queued, you will not be
able to withdraw your account balance below the minimum bond amount.


Bond Forfeiture
---------------

In the event that a caller fails to execute a scheduled call during their
allocated call window, a portion of their bond is forfeited and they are
removed from the caller pool.  The amount forfeited is equal to the current
minimum bond amount.

There are no restrictions on re-entering the caller pool as long as a caller is
willing to put up a new bond.


About Pools
-----------

The caller pool maintains a lists of caller addresses.  Whenever a
change is made to the pool, either addition of a new member or removal of an
existing member, a new generation is queued to take place of the current
generation. 

The new generation will be set to begin 160 blocks in the future.  During the first
80 blocks of this window, other members may leave or join the generation.  The new
generation will be frozen for the 80 blocks leading up to it's starting block.  Each
new generation overlaps the previous generation by 256 blocks.

For example, if we are currently on block 1000, and a member exits the pool.

* The new generation will become active at block 1160
* The new generation will not allow any membership changes after block 1080
* The current generation will be set to end at block 1416 (1160 + 256)
 
Each new generation carries over all of the previous members upon creation.

Once the queued generation becomes active, members are once again allowed to enter
and exit the pool.

Each time a new generation is created, the ordering of its members is shuffled.

.. note::
    It is worth pointing out that from the block during which you exit the
    pool, you must still execute the calls that are allocated to you until the
    current generation has ended.  Failing to do so will cause bond forfeiture.


Entering the Pool
-----------------

An address can enter the caller pool if the following conditions are met.

* The caller has deposited the minimum bond amount into their bond account.
* The caller is not already in the active pool, or the next queued pool.
* The next queued pool does not go active within the next 80 blocks.

To enter the pool, call the ``enterPool`` function on the Caller Pool.

* **Solidity Function Signature:** ``enterPool()``
* **ABI Signature:** ``0x50a3bd39``

If the appropriate conditions are met, you will be added to the next caller
pool.  This will create a new generation if one has not already been created.
Otherwise you will be added to the next queued generation.

You can use the ``canEnterPool`` function to check whether a given address is
currently allowed to enter the pool.

* **Solidity Function Signature:** ``canEnterPool(address callerAddress) returns (bool)``
* **ABI Signature:** ``0x8dd5e298``

Or to to check for the address sending the transaction.

* **Solidity Function Signature:** ``canEnterPool() returns (bool)``
* **ABI Signature:** ``0xc630f92b``


Exiting the Pool
----------------

An address can exit the caller pool if the following conditions are met.

* The caller is in the current active generation.
* The caller has not already exited or been removed from the queued pool (if it
  exists)
* The next queued pool does not go active within the next 80 blocks.

To exit the pool, use the ``exitPool`` function on the Caller Pool.

* **Solidity Function Signature:** ``exitPool()``
* **ABI Signature:** ``0x50a3bd39``

If all conditions are met, a new caller pool will be queued if one has not
already been created and your address will be removed from it.

You can use the ``canExitPool`` function to check whether a given address is
currently allowed to exit the pool.

* **Solidity Function Signature:** ``canExitPool(address callerAddress) returns (bool)``
* **ABI Signature:** ``0xb010d94a``

Alernatively, you can check for the address sending the transaction.

* **Solidity Function Signature:** ``canExitPool(address callerAddress) returns (bool)``
* **ABI Signature:** ``0x5a5383ac``
