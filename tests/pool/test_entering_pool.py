deploy_contracts = [
    "Scheduler",
]


def test_entering_pool(deploy_client, deployed_contracts, deploy_coinbase):
    scheduler = deployed_contracts.Scheduler

    assert scheduler.getBondBalance(deploy_coinbase) == 0
    deposit_amount = scheduler.getMinimumBond() * 10

    txn_1_hash = scheduler.depositBond.sendTransaction(value=deposit_amount)
    deploy_client.wait_for_transaction(txn_1_hash)

    assert scheduler.isInPool(deploy_coinbase) is False
    assert scheduler.canEnterPool(deploy_coinbase) is True

    deploy_client.wait_for_transaction(scheduler.enterPool.sendTransaction())

    # Now queued to be in the next pool.
    assert scheduler.getCurrentGenerationId() == 0
    assert scheduler.isInPool(deploy_coinbase) is True
    assert scheduler.canEnterPool(deploy_coinbase) is False

    next_generation_id = scheduler.getNextGenerationId()
    assert next_generation_id > 0
    assert scheduler.isInGeneration(deploy_coinbase, next_generation_id) is True

    deploy_client.wait_for_block(scheduler.getGenerationStartAt(next_generation_id), 18)

    assert scheduler.isInPool(deploy_coinbase) is True
    assert scheduler.canEnterPool(deploy_coinbase) is False
