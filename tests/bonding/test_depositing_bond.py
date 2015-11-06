deploy_contracts = [
    "Scheduler",
]


def test_depositing_bond(deploy_client, deployed_contracts, deploy_coinbase):
    scheduler = deployed_contracts.Scheduler

    assert scheduler.getBondBalance.call(deploy_coinbase) == 0

    txn_1_hash = scheduler.depositBond.sendTransaction(value=123)
    deploy_client.wait_for_transaction(txn_1_hash)

    assert scheduler.getBondBalance.call(deploy_coinbase) == 123

    txn_2_hash = scheduler.depositBond.sendTransaction(value=456)
    deploy_client.wait_for_transaction(txn_2_hash)

    assert scheduler.getBondBalance.call(deploy_coinbase) == 579
