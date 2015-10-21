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

Use the ``getBondBalance`` function to check the bond balance for the provided
address.

* **Solidity Function Signature:** ``getBondBalance(address callerAddress) returns (uint)``
* **ABI Signature:** ``0x33613cbe``

Or to check the balance of the sender of the transaction.


* **Solidity Function Signature:** ``getBondBalance() returns (uint)``
* **ABI Signature:** ``0x3cbfed74``


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

* **Solidity Function Signature:** ``getDesignatedCaller(bytes32 callKey, uint256 blockNumber)``
* **ABI Signature:** ``0x3c941423``

* **callKey:** specifies the scheduled call.
* **blockNumber:** the block number (during the call window) in question.

This returns the address of the caller who is designated for this block, or
``0x0`` if this call can be executed by anyone on the specified block.
    
Pool Information
----------------

The following functions are available to query information about call pools.

Pool Generations
^^^^^^^^^^^^^^^^

Use the ``getCurrentGenerationId`` function to lookup the id of the pool
generation that is currently active. (returns 0 if no generations exist)

* **Solidity Function Signature:** ``getCurrentGenerationId() returns (uint)``
* **ABI Signature:** ``0xb0171fa4``

Use the ``getNextGenerationId`` function to lookup the generation that is
queued to become active.  Returns ``0x0`` if there is no next generation
queued.

* **Solidity Function Signature:** ``getNextGenerationId() returns (uint)``
* **ABI Signature:** ``0xa502aae8``

Use the ``getGenerationStartAt`` function to lookup the block on which a given
generation will become active.

* **Solidity Function Signature:** ``getGenerationStartAt(uint generationId) returns (uint)``
* **ABI Signature:** ``0xf8b11853``

Use the ``getGenerationEndAt`` function to lookup the block on which a given
generation will end and become inactive.  Returns ``0`` if the generation is
still open ended.

* **Solidity Function Signature:** ``getGenerationEndAt(uint generationId) returns (uint)``
* **ABI Signature:** ``0x306b031d``

Use the ``getGenerationSize`` function to query the number of members in a
given generation.

* **Solidity Function Signature:** ``getGenerationSize(uint generationId) returns (uint)``
* **ABI Signature:** ``0xb3559460``


Get Pool Key for Block
^^^^^^^^^^^^^^^^^^^^^^

Use the ``getGenerationIdForCall`` function to return the ``generationId`` that
should be used for the given call key.  This can be helpful to determine
whether your call execution script should pay attention to specific calls if
you are in the process of entering or exiting the pool.

* **Solidity Function Signature:** ``getGenerationIdForCall(bytes32 callKey) returns (uint)``
* **ABI Signature:** ``0xdb681e54``


Pool Membership
---------------

The following functions can be used to query about an address's pool
membership.

Is In Pool
^^^^^^^^^^

Use the ``isInPool`` function to query whether an address is in either the
currently active generation or the queued generation.

* **Solidity Function Signature:** ``isInPool(address callerAddress) returns (bool)``
* **ABI Signature:** ``0x8baced64``

Or to check whether the current calling address is in the pool.

* **Solidity Function Signature:** ``isInPool() returns (bool)``
* **ABI Signature:** ``0x1ae460e5``

Is In Generation
^^^^^^^^^^^^^^^^

Use the ``isInGeneration`` function to query whether an address is in a
specific generation.

* **Solidity Function Signature:** ``isInGeneration(address callerAddress, uint256 generationId) returns (bool)``
* **ABI Signature:** ``0x7772a380``

Or to query whether the current calling address is in the pool.

* **Solidity Function Signature:** ``isInGeneration(uint256 generationId) returns (bool)``
* **ABI Signature:** ``0xa6c01cfd``


Entering and Exiting Pools
--------------------------

The following functions can be used for actions related to entering and exiting
the call pool.


Can Enter Pool
^^^^^^^^^^^^^^

Use the ``canEnterPool`` function to query whether a given address is allowed to
enter the caller pool.

* **Solidity Function Signature:** ``canEnterPool(address callerAddress) returns (bool)``
* **ABI Signature:** ``0x8dd5e298``

Or to query whether the current calling address is allowed.

* **Solidity Function Signature:** ``canEnterPool() returns (bool)``
* **ABI Signature:** ``0xc630f92b``


Can Exit Pool
^^^^^^^^^^^^^

Use the ``canExitPool`` function to query whether or not you are allowed to
exit the caller pool.

* **Solidity Function Signature:** ``canExitPool(address callerAddress) returns (bool)``
* **ABI Signature:** ``0xb010d94a``

Or to query whether the current calling address is allowed.

* **Solidity Function Signature:** ``canExitPool(address callerAddress) returns (bool)``
* **ABI Signature:** ``0x5a5383ac``


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
