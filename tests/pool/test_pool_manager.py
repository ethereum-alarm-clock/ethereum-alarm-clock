from populus.utils import (
    wait_for_transaction,
    wait_for_block,
)

from alarm_client import (
    PoolManager,
)


def test_pool_manager(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    caller_pool = deployed_contracts.CallerPool

    deposit_amount = caller_pool.getMinimumBond.call() * 10
    # Put in our bond
    wait_for_transaction(
        rpc_client, caller_pool.depositBond.sendTransaction(value=deposit_amount)
    )

    pool_manager = PoolManager(caller_pool)

    assert pool_manager.in_any_pool is False

    pool_manager.monitor_async()

    wait_for_block(rpc_client, rpc_client.get_block_number() + 5, 180)

    first_pool_number = pool_manager.next_pool

    assert first_pool_number > 0
    assert pool_manager.in_any_pool is True
    assert pool_manager.in_next_pool is True

    wait_for_block(rpc_client, first_pool_number + 5, 180)

    # Now leave the pool (like we got kicked out)

    wait_for_transaction(rpc_client, caller_pool.exitPool.sendTransaction())

    second_pool_number = pool_manager.next_pool
    assert second_pool_number > first_pool_number

    # we should not be in the next pool since we left it.
    assert pool_manager.in_next_pool is False

    wait_for_block(rpc_client, second_pool_number + 5, 180)

    # pool manager should have rejoined now that the next pool is live and we
    # aren't in a freeze.
    third_pool_number = pool_manager.next_pool
    assert third_pool_number > second_pool_number

    assert pool_manager.in_active_pool is False
    assert pool_manager.in_next_pool is True
