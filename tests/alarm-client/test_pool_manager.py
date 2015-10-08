from populus.utils import wait_for_transaction, wait_for_block

from eth_alarm_client import (
    PoolManager,
)


deploy_contracts = [
    "CallerPool",
]


def test_pool_manager(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    caller_pool = deployed_contracts.CallerPool

    deposit_amount = caller_pool.getMinimumBond.call() * 10
    # Put in our bond
    wait_for_transaction(
        rpc_client, caller_pool.depositBond.sendTransaction(value=deposit_amount)
    )

    pool_manager = PoolManager(caller_pool)
    block_sage = pool_manager.block_sage

    # should be no pools, nor anyone in them.
    assert pool_manager.active_pool == 0
    assert pool_manager.next_pool == 0
    assert pool_manager.in_any_pool is False
    assert pool_manager.in_next_pool is False
    assert pool_manager.in_active_pool is False

    # check permissions
    assert pool_manager.can_enter_pool is True
    assert pool_manager.can_exit_pool is False

    pool_manager.monitor_async()

    # Wait a few blocks for the pool manager to spin up.
    wait_for_block(rpc_client, rpc_client.get_block_number() + 5, 60)

    first_pool = pool_manager.next_pool

    # should have initiated joining the next pool but won't be in it yet.
    assert pool_manager.active_pool == 0
    assert first_pool > 0
    assert pool_manager.in_any_pool is True
    assert pool_manager.in_next_pool is True
    assert pool_manager.in_active_pool is False

    # check permissions
    assert pool_manager.can_enter_pool is False
    assert pool_manager.can_exit_pool is False

    # Wait for the pool to become active.
    wait_for_block(
        rpc_client,
        first_pool,
        block_sage.estimated_time_to_block(first_pool) * 2,
    )

    # we should now be in the active pool.
    assert pool_manager.active_pool == first_pool
    assert pool_manager.next_pool == 0
    assert pool_manager.in_any_pool is True
    assert pool_manager.in_next_pool is False
    assert pool_manager.in_active_pool is True

    # check permissions
    assert pool_manager.can_enter_pool is False
    assert pool_manager.can_exit_pool is True

    # Now we manually remove ourselves.
    wait_for_transaction(rpc_client, caller_pool.exitPool.sendTransaction())

    second_pool_key = pool_manager.next_pool

    # New pool should have been formed.
    assert second_pool_key > first_pool

    # Current status should not have changed except that the next pool has now
    # been formed but we aren't in it.
    assert pool_manager.in_any_pool is True
    assert pool_manager.in_next_pool is False
    assert pool_manager.in_active_pool is True

    # Wait for the next pool to become active plus a little.
    wait_for_block(
        rpc_client,
        second_pool_key,
        block_sage.estimated_time_to_block(second_pool_key) * 2,
    )

    # The manager should have rejoined.
    assert pool_manager.active_pool == second_pool_key
