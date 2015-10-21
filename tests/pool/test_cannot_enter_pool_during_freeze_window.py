from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "JoinsPool",
]


def test_pool_membership_frozen_during_transition_period(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    joiner = deployed_contracts.JoinsPool
    coinbase = deploy_client.get_coinbase()

    wait_for_transaction(deploy_client, joiner.setCallerPool.sendTransaction(alarm._meta.address))

    assert alarm.getBondBalance(coinbase) == 0
    deposit_amount = alarm.getMinimumBond() * 10
    # Put in our bond
    wait_for_transaction(
        deploy_client, alarm.depositBond.sendTransaction(value=deposit_amount)
    )

    # Put the contract's bond in
    wait_for_transaction(
        deploy_client,
        deploy_client.send_transaction(to=joiner._meta.address, value=deposit_amount)
    )
    wait_for_transaction(
        deploy_client, joiner.deposit.sendTransaction(deposit_amount)
    )
    wait_for_transaction(deploy_client, joiner.enter.sendTransaction())

    # New pool is formed but not active
    first_generation_id = alarm.getNextGenerationId()
    assert first_generation_id > 0

    # Only the contract is in the pool. (but it isn't active yet)
    assert alarm.getCurrentGenerationId() == 0
    assert alarm.isInGeneration(joiner._meta.address, first_generation_id) is True
    assert alarm.isInGeneration(coinbase, first_generation_id) is False

    # Both are in the pool but it isn't active yet
    assert alarm.getCurrentGenerationId() == 0
    assert alarm.getNextGenerationId() == first_generation_id
    assert alarm.isInGeneration(joiner._meta.address, first_generation_id) is True
    assert alarm.isInGeneration(coinbase, first_generation_id) is False

    # Wait for it to become active
    deploy_client.wait_for_block(alarm.getGenerationStartAt(first_generation_id), 180)
    assert alarm.getCurrentGenerationId() == first_generation_id
    assert alarm.getNextGenerationId() == 0

    # Now the contract leaves the pool.
    wait_for_transaction(deploy_client, joiner.exit.sendTransaction())
    second_generation_id = alarm.getNextGenerationId()

    # New pool should have been setup
    assert second_generation_id > first_generation_id

    # joiner should not be in next pool.
    assert alarm.isInGeneration(joiner._meta.address, second_generation_id) is False

    # should not be in the pool until it becomes active
    assert alarm.isInGeneration(joiner._meta.address, first_generation_id) is True
    assert alarm.isInGeneration(coinbase, first_generation_id) is False

    # should still be allowed to enter
    assert alarm.canEnterPool(coinbase) is True

    # wait for the pool to become active
    freeze_duration = alarm.getPoolFreezePeriod()
    deploy_client.wait_for_block(alarm.getGenerationStartAt(second_generation_id) - freeze_duration, 180)

    # should no longer be allowed to leave (within freeze window)
    assert alarm.canEnterPool(coinbase) is False

    # wait for the pool to become active
    deploy_client.wait_for_block(alarm.getGenerationStartAt(second_generation_id), 180)

    # should now be allowed to leave.
    assert alarm.canEnterPool(coinbase) is True
