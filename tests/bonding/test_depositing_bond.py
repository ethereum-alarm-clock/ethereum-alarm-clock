from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
]


def test_depositing_bond(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    coinbase = deploy_client.get_coinbase()

    assert alarm.getBondBalance.call(coinbase) == 0

    txn_1_hash = alarm.depositBond.sendTransaction(value=123)
    wait_for_transaction(deploy_client, txn_1_hash)

    assert alarm.getBondBalance.call(coinbase) == 123

    txn_2_hash = alarm.depositBond.sendTransaction(value=456)
    wait_for_transaction(deploy_client, txn_2_hash)

    assert alarm.getBondBalance.call(coinbase) == 579
