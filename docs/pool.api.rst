Caller Pool API
===============

The Caller Pool contract exposes the following api functions.

Bond Management
---------------

The following functions are available for managing the ether deposited as a
bond with the Caller Pool.

Get Minimum Bond
^^^^^^^^^^^^^^^^

Use the ``getMinimumBond`` function to retrieve the current minimum bond value
required to be able to enter the caller pool.

* **Solidity Function Signature:** ``getMinimumBond() returns (uint)``
* **ABI Signature:** ``0x23306ed6``

Check Bond Balance
^^^^^^^^^^^^^^^^^^

Use the ``callerBonds`` function to check the bond balance for the provided
address.

* **Solidity Function Signature:** ``callerBonds(address callerAddress) returns (uint)``
* **ABI Signature:** ``0xc861cd66``

Deposit Bond
^^^^^^^^^^^^

Use the ``depositBond`` function to deposit you bond with the caller pool.

* **Solidity Function Signature:** ``depositBond()``
* **ABI Signature:** ``0x741b3c39``

Withdraw Bond
^^^^^^^^^^^^^

Use the ``withdrawBond`` function to withdraw funds from your bond.

* **Solidity Function Signature:** ``withdrawBond()``
* **ABI Signature:** ``0xc3daab96``

When in either an active or queued caller pool, you cannot withdraw your
account below the minimum bond value.

Call Scheduling and Execution
-----------------------------

The following function is available for callers.

Get Designated Caller
^^^^^^^^^^^^^^^^^^^^^

Use the ``getDesignatedCaller`` function to retrieve which caller address, if
any, is designated as the caller for a given block and scheduled call.

* **Solidity Function Signature:** ``getDesignatedCaller(bytes32 callKey, uint targetBlock, uint8 gracePeriod, uint blockNumber) public returns (address)``
* **ABI Signature:** ``0xe8543d0d``

* **callKey:** specifies the scheduled call.
* **targetBlock:** the target block for the specified call.
* **gracePeriod:** the grace period for the specified call.
* **blockNumber:** the block number (during the call window) in question.

This returns the address of the caller who is designated for this block, or
``0x0`` if this call can be executed by anyone on the specified block.
    
Pool Information
----------------

The following functions are available to query information about call pools.

Pool History
^^^^^^^^^^^^

Use the ``poolHistory`` function to lookup historical caller pools.

* **Solidity Function Signature:** ``poolHistory(uint index) returns (uint)``
* **ABI Signature:** ``0x910789c4``

This function can be used to return the nth caller pool, where index is the
0-indexed number of the desired caller pool.  Returns the ``poolKey`` which can
be used to reference the caller pool.  The ``poolKey`` is also the block number
that the pool became active.

Get Pool Key for Block
^^^^^^^^^^^^^^^^^^^^^^

Use the ``getPoolKeyForBlock`` function to return the ``poolKey`` that should
be used for the given block number.

* **Solidity Function Signature:** ``getPoolKeyForBlock(uint blockNumber) returns (uint)``
* **ABI Signature:** ``0xaec918c7``

Get Active Pool Key
^^^^^^^^^^^^^^^^^^^

Use the ``getActivePoolKey`` function to retrieve the ``poolKey`` for the
caller pool that is currently active.

* **Solidity Function Signature:** ``getActivePoolKey() returns (uint)``
* **ABI Signature:** ``0xa6814e8e``


Get Next Pool Key
^^^^^^^^^^^^^^^^^

Use the ``getNextPoolKey`` function to retrieve the ``poolKey`` that is
currently queued up next.

* **Solidity Function Signature:** ``getNextPoolKey() returns (uint)``
* **ABI Signature:** ``0xc4afc3fb``

Returns ``0`` if there is no caller pool queued.

Get Pool Size
^^^^^^^^^^^^^

Use the ``getPoolSize`` function to lookup the size of a given pool.

* **Solidity Function Signature:** ``getPoolSize(uint poolKey) returns (uint)``
* **ABI Signature:** ``0x6595f73a``

Pool Membership
---------------

The following functions can be used to query about an address's pool
membership.

Is In Any Pool
^^^^^^^^^^^^^^

Use the ``isInAnyPool`` function to query whether an address is in either the
currently active caller pool or the queued caller pool.

* **Solidity Function Signature:** ``isInAnyPool(address callerAddress) returns (bool)``
* **ABI Signature:** ``0x84c92c9a``

Is In Pool
^^^^^^^^^^

Use the ``isInPool`` function to query whether an address is in a specific pool.

* **Solidity Function Signature:** ``isInPool(address callerAddress, uint poolKey) returns (bool)``
* **ABI Signature:** ``0x19f74e1f``


Entering and Exiting Pools
--------------------------

The following functions can be used for actions related to entering and exiting
the call pool.


Can Enter Pool
^^^^^^^^^^^^^^

Use the ``canEnterPool`` function to query whether or not you are allowed to
enter the caller pool.

* **Solidity Function Signature:** ``canEnterPool() returns (bool)``
* **ABI Signature:** ``0x8dd5e298``


Can Exit Pool
^^^^^^^^^^^^^

Use the ``canExitPool`` function to query whether or not you are allowed to
exit the caller pool.

* **Solidity Function Signature:** ``canExitPool() returns (bool)``
* **ABI Signature:** ``0xb010d94a``


Enter Pool
^^^^^^^^^^

Use the ``enterPool`` function to enter the caller pool.

* **Solidity Function Signature:** ``enterPool() returns (bool)``
* **ABI Signature:** ``0x50a3bd39``

Exit Pool
^^^^^^^^^

Use the ``exitPool`` function to exit the caller pool.

* **Solidity Function Signature:** ``exitPool() returns (bool)``
* **ABI Signature:** ``0x29917954``
