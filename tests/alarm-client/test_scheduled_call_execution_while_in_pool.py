from populus.contracts import get_max_gas
from populus.utils import (
    wait_for_transaction,
    wait_for_block,
)

from eth_alarm_client import (
    PoolManager,
    ScheduledCall,
)


deploy_contracts = [
    "Alarm",
    "Grove",
    "JoinsPool",
    "SpecifyBlock",
]


def test_scheduled_call_execution_with_pool(geth_node, geth_coinbase, rpc_client, deployed_contracts, contracts):
    alarm = deployed_contracts.Alarm
    joiner = deployed_contracts.JoinsPool
    client_contract = deployed_contracts.SpecifyBlock
    caller_pool = contracts.CallerPool(alarm.getCallerPoolAddress.call(), rpc_client)

    # Put in our deposit with the alarm contract.
    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    wait_for_transaction(rpc_client, joiner.setCallerPool.sendTransaction(caller_pool._meta.address))

    assert caller_pool.callerBonds.call(geth_coinbase) == 0
    deposit_amount = caller_pool.getMinimumBond.call() * 10
    # Put in our bond
    wait_for_transaction(
        rpc_client, caller_pool.depositBond.sendTransaction(value=deposit_amount)
    )

    # Put the contract's bond in
    wait_for_transaction(
        rpc_client,
        rpc_client.send_transaction(to=joiner._meta.address, value=deposit_amount)
    )
    wait_for_transaction(
        rpc_client, joiner.deposit.sendTransaction(deposit_amount)
    )

    # Both join the pool
    wait_for_transaction(rpc_client, joiner.enter.sendTransaction())
    wait_for_transaction(rpc_client, caller_pool.enterPool.sendTransaction())

    # New pool is formed but not active
    first_pool_key = caller_pool.getNextPoolKey.call()
    assert first_pool_key > 0

    # Go ahead and schedule the call.
    target_block = first_pool_key + 5

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, target_block)
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    # Wait for the pool to become active
    wait_for_block(rpc_client, first_pool_key, 180)

    # We should both be in the pool
    assert caller_pool.getActivePoolKey.call() == first_pool_key
    assert caller_pool.isInPool.call(joiner._meta.address, first_pool_key) is True
    assert caller_pool.isInPool.call(geth_coinbase, first_pool_key) is True

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    pool_manager = PoolManager(caller_pool)
    scheduled_call = ScheduledCall(alarm, pool_manager, callKey)

    scheduled_call.execute_async()

    wait_for_block(rpc_client, scheduled_call.target_block + 8, 180)

    assert scheduled_call.txn_hash
    assert scheduled_call.txn_receipt
    assert scheduled_call.txn

    assert scheduled_call.was_called
    assert alarm.checkIfCalled.call(scheduled_call.call_key)
    assert scheduled_call.target_block <= scheduled_call.called_at_block
    assert scheduled_call.called_at_block <= scheduled_call.target_block + scheduled_call.grace_period
