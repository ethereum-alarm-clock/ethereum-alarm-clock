from populus.utils import wait_for_transaction


def test_depositing_funds(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    coinbase = deploy_client.get_coinbase()

    assert alarm.getAccountBalance.call(coinbase) == 0

    txn_1_hash = alarm.deposit.sendTransaction(coinbase, value=123)
    wait_for_transaction(alarm._meta.rpc_client, txn_1_hash)

    assert alarm.getAccountBalance.call(coinbase) == 123

    txn_2_hash = alarm.deposit.sendTransaction(coinbase, value=456)
    wait_for_transaction(alarm._meta.rpc_client, txn_2_hash)

    assert alarm.getAccountBalance.call(coinbase) == 579
