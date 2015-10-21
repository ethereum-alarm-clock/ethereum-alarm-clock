from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
]


def test_exiting_pool(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    coinbase = deploy_client.get_coinbase()

    assert alarm.getBondBalance(coinbase) == 0
    deposit_amount = alarm.getMinimumBond() * 10

    txn_1_hash = alarm.depositBond.sendTransaction(value=deposit_amount)
    wait_for_transaction(deploy_client, txn_1_hash)

    assert alarm.getCurrentGenerationId() == 0
    assert alarm.getNextGenerationId() == 0
    assert alarm.isInPool(coinbase) is False
    assert alarm.canEnterPool(coinbase) is True
    assert alarm.canExitPool(coinbase) is False

    wait_for_transaction(deploy_client, alarm.enterPool.sendTransaction())
    first_generation_id = alarm.getNextGenerationId()
    deploy_client.wait_for_block(alarm.getGenerationStartAt(first_generation_id), 180)

    assert alarm.getCurrentGenerationId() == first_generation_id
    assert alarm.getNextGenerationId() == 0
    assert alarm.isInPool(coinbase) is True
    assert alarm.isInGeneration(coinbase, first_generation_id) is True
    assert alarm.canEnterPool(coinbase) is False
    assert alarm.canExitPool(coinbase) is True

    wait_for_transaction(deploy_client, alarm.exitPool.sendTransaction())
    second_generation_id = alarm.getNextGenerationId()

    assert second_generation_id > first_generation_id
    assert alarm.isInPool(coinbase) is True
    assert alarm.isInGeneration(coinbase, first_generation_id) is True

    deploy_client.wait_for_block(alarm.getGenerationEndAt(first_generation_id), 180)

    assert alarm.getCurrentGenerationId() == second_generation_id
    assert alarm.getNextGenerationId() == 0
    assert alarm.isInPool(coinbase) is False
    assert alarm.canEnterPool(coinbase) is True
    assert alarm.canExitPool(coinbase) is False
