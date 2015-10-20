from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
]


def test_withdrawing_bond_restricted_when_in_pool(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    coinbase = deploy_client.get_coinbase()

    assert alarm.getBondBalance(coinbase) == 0
    deposit_amount = alarm.getMinimumBond() * 10

    txn_1_hash = alarm.depositBond.sendTransaction(value=deposit_amount)
    wait_for_transaction(deploy_client, txn_1_hash)

    assert alarm.getBondBalance(coinbase) == deposit_amount

    assert alarm.isInPool(coinbase) is False
    assert alarm.canEnterPool(coinbase) is True
    wait_for_transaction(deploy_client, alarm.enterPool.sendTransaction())

    txn_2_hash = alarm.withdrawBond.sendTransaction(deposit_amount)
    wait_for_transaction(deploy_client, txn_2_hash)

    assert alarm.isInPool(coinbase) is True

    # Withdrawl of full amount not allowed
    assert alarm.getBondBalance(coinbase) == deposit_amount

    # wi
    minimum_bond = alarm.getMinimumBond()
    txn_3_hash = alarm.withdrawBond.sendTransaction(
        deposit_amount - 2 * minimum_bond,
    )
    wait_for_transaction(deploy_client, txn_3_hash)

    # Withdrawl of amount above minimum bond amount is allowed
    assert alarm.isInPool(coinbase) is True
    assert alarm.getBondBalance(coinbase) == 2 * minimum_bond
