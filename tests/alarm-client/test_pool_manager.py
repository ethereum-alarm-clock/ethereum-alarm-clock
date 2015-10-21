import time

from populus.utils import wait_for_transaction, wait_for_block

from eth_alarm_client import (
    PoolManager,
)


deploy_contracts = [
    "Alarm",
]


def test_pool_manager(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    coinbase = deploy_client.get_coinbase()

    deposit_amount = alarm.getMinimumBond.call() * 10

    # Put in our bond
    wait_for_transaction(
        deploy_client, alarm.depositBond.sendTransaction(value=deposit_amount)
    )

    pool_manager = PoolManager(alarm)
    block_sage = pool_manager.block_sage

    # should be no pools, nor anyone in them.
    assert pool_manager.current_generation_id == 0
    assert pool_manager.next_generation_id == 0
    assert pool_manager.in_any_pool is False
    assert pool_manager.in_next_generation is False
    assert pool_manager.in_current_generation is False

    # check permissions
    assert pool_manager.can_enter_pool is True
    assert pool_manager.can_exit_pool is False

    pool_manager.monitor_async()

    # Wait a few blocks for the pool manager to spin up.
    for _ in range(5):
        deploy_client.evm.mine()

    time.sleep(5)

    first_generation_id = pool_manager.next_generation_id

    # should have initiated joining the next pool but won't be in it yet.
    assert pool_manager.current_generation_id == 0
    assert first_generation_id > 0
    assert pool_manager.in_any_pool is True
    assert pool_manager.in_next_generation is True
    assert pool_manager.in_current_generation is False

    # check permissions
    assert pool_manager.can_enter_pool is False
    assert pool_manager.can_exit_pool is False

    # Wait for the pool to become active.
    for _ in range(deploy_client.get_block_number(), pool_manager.next_generation_start_at):

        deploy_client.evm.mine()

    # we should now be in the active pool.
    assert pool_manager.current_generation_id == first_generation_id
    assert pool_manager.next_generation_id == 0
    assert pool_manager.in_any_pool is True
    assert pool_manager.in_next_generation is False
    assert pool_manager.in_current_generation is True

    # check permissions
    assert pool_manager.can_enter_pool is False
    assert pool_manager.can_exit_pool is True

    # Now we manually remove ourselves.
    wait_for_transaction(deploy_client, alarm.exitPool.sendTransaction())

    second_generation_id = pool_manager.next_generation_id

    # New pool should have been formed.
    assert second_generation_id > first_generation_id

    # Current status should not have changed except that the next pool has now
    # been formed but we aren't in it.
    assert pool_manager.in_any_pool is True
    assert pool_manager.in_next_generation is False
    assert pool_manager.in_current_generation is True

    # Wait for the next pool to become active plus a little.
    first_generation_end = alarm.getGenerationEndAt(first_generation_id)
    deploy_client.wait_for_block(
        first_generation_end,
        block_sage.estimated_time_to_block(first_generation_end) * 2,
    )

    # The manager should have rejoined.
    assert pool_manager.current_generation_id == second_generation_id
