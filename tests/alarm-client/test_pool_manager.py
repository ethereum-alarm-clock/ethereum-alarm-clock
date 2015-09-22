from ethereum import utils

from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction, wait_for_block

from alarm_client import (
    PoolManager,
)


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_pool_manager(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    caller_pool = deployed_contracts.CallerPool

    pool_manager = PoolManager(caller_pool)

    # should be no pools, nor anyone in them.
    assert pool_manager.active_pool == 0
    assert pool_manager.next_pool == 0
    assert pool_manager.in_any_pool is False
    assert pool_manager.in_next_pool is False
    assert pool_manager.in_active_pool is False

    # check permissions
    assert pool_manager.can_enter_pool is True
    assert pool_manager.can_exit_pool is False

    pool_manager.run_async()

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
    wait_for_block(rpc_client, first_pool)

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
    wait_for_block(rpc_client, second_pool_key + 5)

    # The manager should have rejoined.
    assert pool_manager.active_pool == second_pool_key
    assert False
