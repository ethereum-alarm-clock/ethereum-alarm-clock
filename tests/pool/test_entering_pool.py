from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
]


def test_entering_pool(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    coinbase = deploy_client.get_coinbase()

    assert alarm.getBondBalance(coinbase) == 0
    deposit_amount = alarm.getMinimumBond() * 10

    txn_1_hash = alarm.depositBond.sendTransaction(value=deposit_amount)
    wait_for_transaction(deploy_client, txn_1_hash)

    assert alarm.isInPool(coinbase) is False
    assert alarm.canEnterPool(coinbase) is True

    wait_for_transaction(deploy_client, alarm.enterPool.sendTransaction())

    # Now queued to be in the next pool.
    assert alarm.getCurrentGenerationId() == 0
    assert alarm.isInPool(coinbase) is True
    assert alarm.canEnterPool(coinbase) is False

    next_generation_id = alarm.getNextGenerationId()
    assert next_generation_id > 0
    assert alarm.isInGeneration(coinbase, next_generation_id) is True

    deploy_client.wait_for_block(alarm.getGenerationStartAt(next_generation_id), 18)

    assert alarm.isInPool(coinbase) is True
    assert alarm.canEnterPool(coinbase) is False
