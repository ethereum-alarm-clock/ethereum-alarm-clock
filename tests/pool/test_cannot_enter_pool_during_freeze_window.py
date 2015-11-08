deploy_contracts = [
    "Scheduler",
    "JoinsPool",
]


def test_pool_membership_frozen_during_transition_period(deploy_client,
                                                         deployed_contracts,
                                                         deploy_coinbase):
    scheduler = deployed_contracts.Scheduler
    joiner = deployed_contracts.JoinsPool

    deploy_client.wait_for_transaction(
        joiner.setCallerPool.sendTransaction(scheduler._meta.address)
    )

    assert scheduler.getBondBalance(deploy_coinbase) == 0
    deposit_amount = scheduler.getMinimumBond() * 10
    # Put in our bond
    deploy_client.wait_for_transaction(
        scheduler.depositBond.sendTransaction(value=deposit_amount)
    )

    # Put the contract's bond in
    deploy_client.wait_for_transaction(
        deploy_client.send_transaction(to=joiner._meta.address, value=deposit_amount)
    )
    deploy_client.wait_for_transaction(
        joiner.deposit.sendTransaction(deposit_amount)
    )
    deploy_client.wait_for_transaction(joiner.enter.sendTransaction())

    # New pool is formed but not active
    first_generation_id = scheduler.getNextGenerationId()
    assert first_generation_id > 0

    # Only the contract is in the pool. (but it isn't active yet)
    assert scheduler.getCurrentGenerationId() == 0
    assert scheduler.isInGeneration(joiner._meta.address, first_generation_id) is True
    assert scheduler.isInGeneration(deploy_coinbase, first_generation_id) is False

    # Both are in the pool but it isn't active yet
    assert scheduler.getCurrentGenerationId() == 0
    assert scheduler.getNextGenerationId() == first_generation_id
    assert scheduler.isInGeneration(joiner._meta.address, first_generation_id) is True
    assert scheduler.isInGeneration(deploy_coinbase, first_generation_id) is False

    # Wait for it to become active
    deploy_client.wait_for_block(scheduler.getGenerationStartAt(first_generation_id), 180)
    assert scheduler.getCurrentGenerationId() == first_generation_id
    assert scheduler.getNextGenerationId() == 0

    # Now the contract leaves the pool.
    deploy_client.wait_for_transaction(joiner.exit.sendTransaction())
    second_generation_id = scheduler.getNextGenerationId()

    # New pool should have been setup
    assert second_generation_id > first_generation_id

    # joiner should not be in next pool.
    assert scheduler.isInGeneration(joiner._meta.address, second_generation_id) is False

    # should not be in the pool until it becomes active
    assert scheduler.isInGeneration(joiner._meta.address, first_generation_id) is True
    assert scheduler.isInGeneration(deploy_coinbase, first_generation_id) is False

    # should still be allowed to enter
    assert scheduler.canEnterPool(deploy_coinbase) is True

    # wait for the pool to become active
    freeze_duration = scheduler.getPoolFreezePeriod()
    deploy_client.wait_for_block(scheduler.getGenerationStartAt(second_generation_id) - freeze_duration, 180)

    # should no longer be allowed to leave (within freeze window)
    assert scheduler.canEnterPool(deploy_coinbase) is False

    # wait for the pool to become active
    deploy_client.wait_for_block(scheduler.getGenerationStartAt(second_generation_id), 180)

    # should now be allowed to leave.
    assert scheduler.canEnterPool(deploy_coinbase) is True
