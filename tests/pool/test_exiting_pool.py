deploy_contracts = [
    "Scheduler",
]


def test_exiting_pool(deploy_client, deployed_contracts, deploy_coinbase):
    scheduler = deployed_contracts.Scheduler

    assert scheduler.getBondBalance(deploy_coinbase) == 0
    deposit_amount = scheduler.getMinimumBond() * 10

    txn_1_hash = scheduler.depositBond.sendTransaction(value=deposit_amount)
    deploy_client.wait_for_transaction(txn_1_hash)

    assert scheduler.getCurrentGenerationId() == 0
    assert scheduler.getNextGenerationId() == 0
    assert scheduler.isInPool(deploy_coinbase) is False
    assert scheduler.canEnterPool(deploy_coinbase) is True
    assert scheduler.canExitPool(deploy_coinbase) is False

    deploy_client.wait_for_transaction(scheduler.enterPool.sendTransaction())
    first_generation_id = scheduler.getNextGenerationId()
    deploy_client.wait_for_block(scheduler.getGenerationStartAt(first_generation_id), 180)

    assert scheduler.getCurrentGenerationId() == first_generation_id
    assert scheduler.getNextGenerationId() == 0
    assert scheduler.isInPool(deploy_coinbase) is True
    assert scheduler.isInGeneration(deploy_coinbase, first_generation_id) is True
    assert scheduler.canEnterPool(deploy_coinbase) is False
    assert scheduler.canExitPool(deploy_coinbase) is True

    deploy_client.wait_for_transaction(scheduler.exitPool.sendTransaction())
    second_generation_id = scheduler.getNextGenerationId()

    assert second_generation_id > first_generation_id
    assert scheduler.isInPool(deploy_coinbase) is True
    assert scheduler.isInGeneration(deploy_coinbase, first_generation_id) is True

    deploy_client.wait_for_block(scheduler.getGenerationEndAt(first_generation_id), 180)

    assert scheduler.getCurrentGenerationId() == second_generation_id
    assert scheduler.getNextGenerationId() == 0
    assert scheduler.isInPool(deploy_coinbase) is False
    assert scheduler.canEnterPool(deploy_coinbase) is True
    assert scheduler.canExitPool(deploy_coinbase) is False
