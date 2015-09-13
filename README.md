# Ethereum Alarm Clock

Alarm allows scheduling of function calls on a contract at a specified block in
the future.

## QuickStart

Consider the following contract which we want to blow up one hour after it is
created.


```
contract AlarmAPI {
        function scheduleCall(address to, bytes4 signature, bytes32 dataHash, uint targetBlock) public returns (bytes32);
}

contract Bomb {
    function Bomb() {
        // instantiate an instance of the AlarmAPI pointed at the Alarm contract.
        AlarmAPI alarm = AlarmAPI(0x.....);
        // schedule a call to the `explode` function to be executed 240 blocks
        // (1 hour) in the future.
        alarm.scheduleCall(address(this), bytes4(sha3("explode()")), sha3(), block.number + 240)
    }

    function explode() {
        suicide(...);
    }
}
```

## Call Scheduling

Scheduling a function call and having it executed at the desired time in the
future requires the following things.

1. The address that schedules the call must have a sufficient account balance
   to cover the maximum possible gas usage.
2. If the function call requires call data, that data must be registered.

The easiest way to interact with the Alarm contract is to use the following
contract in your code.

```
contract AlarmAPI {
    /*
     *  This contract allows you to interact with the Alarm contract
     *  without having to use `address.call(...)`.
     *
     *  param to:
     *      the address of the contract the call should be executed on.
     *      This is currently required to be the same as `msg.sender`
     *  param signature:
     *      The bytes4 signature of the function that should be called.
     *  param dataHash:
     *      The sha3() of the call data that the function should be called
     *      with.  (this data must have already been registered through the
     *      `registerData` api.
     *  param targetBlock:
     *      The block number that the call should be executed on.
     */
    function scheduleCall(address to, bytes4 signature, bytes32 dataHash, uint targetBlock) public returns (bytes32);
```

## Registering Call Data

If a scheduled function call requires call data to be passed, that data must be
registered ahead of time.  This currently must be done via `address.call` with
the ABI signature for the `registerData()` funcion (`0xb0f07e44`) followed by
the arguments that should be passed to the function call.

```
contract MoneyBomb {
    function lightFuse() {
        address alarm = 0x...;
        alarm.call(bytes4(sha3("registerData()")), target)
        // Then we'd need to actually schedule the call...
        ...
    }

    function explode(address target) {
        suicide(target);
    }
}
```

Once data has been registered once, it does not need to be registered again for
subsequent call scheduling.


## Call Keys

Each scheduled call is assigned a `callKey` which is equal to 
`sha3(to, signature, dataHash, targetBlock)` where:

- `to` is the contract address the function should be called on.
- `signature` is th ABI signature of the function that should be called.
- `dataHash` is the `sha3` of the call data that should be passed in.
- `targetBlock` is the block number that the call should be executed on.

The call key can be used to query information about a scheduled call.


## Querying Scheduled Call Information

The following API is available for querying information about scheduled calls.
Note that each of these requires passing in the call key for the desired
scheduled call.

- `getCallTargetAddress(bytes32 callKey) public returns (address)`

    Returns the contract address that the call will be executed on.

- `getCallScheduledBy(bytes32 callKey) public returns (address)`

    Returns the address that scheduled the call.

- `getCallCalledAtBlock(bytes32 callKey) public returns (uint)`

    Returns the block that the call was executed on (or `0` if the call has not been executed).

- `getCallTargetBlock(bytes32 callKey) public returns (uint)`

    Returns the block that the call is scheduled for.

- `getCallGasPrice(bytes32 callKey) public returns (uint)`

    Returns the gas price paid for the transaction in which the call was executed.

- `getCallGasUsed(bytes32 callKey) public returns (uint)`

    Returns the amount of gas used executing the call.  (Note that this number
    does not include the full gas used in the transaction that was used to
    execute the call.)

- `getCallSignature(bytes32 callKey) public returns (bytes4)`

    Returns the ABI function signature for scheduled call.

- `checkIfCalled(bytes32 callKey) public returns (bool)`

    Returns whether or not the call has been executed.

- `checkIfSuccess(bytes32 callKey) public returns (bool)`

    Returns the result of `call(...)` when the call was executed.

- `getDataHash(bytes32 callKey) public returns (bytes32)`

    Returns the `sha3` hash of the data for the scheduled call.

- `getCallPayout(bytes32 callKey) public returns (uint)`

    Returns the amount (in wei) that was paid to the address which executed the call.

- `getCallProfit(bytes32 callKey) public returns (uint)`

    Returns the amount (in wei) that was kept as a scheduling fee.


## Account Management API


Scheduled function calls must be paid for by the caller.  Alarm requires those
scheduling a call to pay for it in advance.  This is done by maintaining an
account balance with Alarm.

At the time of execution, the account belonging to the scheduler must have a
balance of at least the the maximum possible transaction cost plus fees.

Maximum transaction cost is computed from `gasLimit * gasPrice` where
`gasLimit` is the maximum gas allowed in the block during which the call is
executed, and `gasPrice` is the cost of gas for the transaction in which the
call is executed.

The following API is available for managing your account with Alarm.

- `deposit(address accountAddress)`

    Addes the `value` (in wei) of the transaction to the `accountAddress`.

- `withdraw(uint value)`

    Sends the `value` (in wei) to `msg.sender`.  This amount is deducted from
    the `msg.sender`'s account.  The account must have a sufficient balance for
    the transaction to go through.

- `accountBalances(address accountAddress) returns (uint)`

    Returns the account balance for the provided `accountAddress`.


## Fees

Alarm charges a fee for execution of scheduled function calls.  This fee is 2%
of total cost of gas for the executing transaction.  This fee is split evenly
between the executor of the call and the Alarm service.

It should be noted that there is some administrative overhead for scheduled
calls.  The Alarm service must do things like tracking account balances and
recording gas usage and meta data about the call.


## Executing Calls

Operators of ethereum addresses can earn
