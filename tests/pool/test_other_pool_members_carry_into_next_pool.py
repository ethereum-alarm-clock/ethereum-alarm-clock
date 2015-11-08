deploy_contracts = [
    "Scheduler",
    "JoinsPool",
]


def test_pool_membership_is_carried_over(deploy_client, deployed_contracts, deploy_coinbase):
    scheduler = deployed_contracts.Scheduler
    joiner = deployed_contracts.JoinsPool

    deploy_client.wait_for_transaction(joiner.setCallerPool(scheduler._meta.address))

    assert scheduler.getBondBalance(deploy_coinbase) == 0
    deposit_amount = scheduler.getMinimumBond() * 10
    # Put in our bond
    deploy_client.wait_for_transaction(
        scheduler.depositBond(value=deposit_amount)
    )

    # Put the contract's bond in
    deploy_client.wait_for_transaction(
        deploy_client.send_transaction(to=joiner._meta.address, value=deposit_amount)
    )
    deploy_client.wait_for_transaction(
        joiner.deposit(deposit_amount)
    )
    deploy_client.wait_for_transaction(joiner.enter())

    # New pool is formed but not active
    first_generation_id = scheduler.getNextGenerationId()
    assert first_generation_id > 0

    # Only the contract is in the pool. (but it isn't active yet)
    assert scheduler.getCurrentGenerationId() == 0
    assert scheduler.isInGeneration(joiner._meta.address, first_generation_id) is True
    assert scheduler.isInGeneration(deploy_coinbase, first_generation_id) is False

    # Now we join the pool
    deploy_client.wait_for_transaction(scheduler.enterPool())

    # Both are in the pool but it isn't active yet
    assert scheduler.getCurrentGenerationId() == 0
    assert scheduler.getNextGenerationId() == first_generation_id
    assert scheduler.isInGeneration(joiner._meta.address, first_generation_id) is True
    assert scheduler.isInGeneration(deploy_coinbase, first_generation_id) is True

    # Wait for it to become active
    deploy_client.wait_for_block(scheduler.getGenerationStartAt(first_generation_id), 180)
    assert scheduler.getCurrentGenerationId() == first_generation_id
    assert scheduler.getNextGenerationId() == 0

    # Now the contract leaves the pool.
    deploy_client.wait_for_transaction(joiner.exit())
    second_generation_id = scheduler.getNextGenerationId()

    # New pool should have been setup
    assert second_generation_id > first_generation_id

    # should still be in the pool until it becomes active
    assert scheduler.isInGeneration(joiner._meta.address, first_generation_id) is True
    assert scheduler.isInGeneration(deploy_coinbase, first_generation_id) is True

    # wait for the pool to become active
    deploy_client.wait_for_block(scheduler.getGenerationEndAt(first_generation_id), 180)

    # contract shouldn't be in the pool anymore but we should.
    assert scheduler.getCurrentGenerationId() == second_generation_id
    assert scheduler.getNextGenerationId() == 0
    assert scheduler.isInGeneration(joiner._meta.address, second_generation_id) is False
    assert scheduler.isInGeneration(deploy_coinbase, second_generation_id) is True
