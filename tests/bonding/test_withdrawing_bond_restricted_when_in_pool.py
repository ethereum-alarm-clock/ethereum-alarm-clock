deploy_contracts = [
    "Scheduler",
]


def test_withdrawing_bond_restricted_when_in_pool(deploy_client, deployed_contracts, deploy_coinbase):
    scheduler = deployed_contracts.Scheduler

    assert scheduler.getBondBalance(deploy_coinbase) == 0
    deposit_amount = scheduler.getMinimumBond() * 10

    txn_1_hash = scheduler.depositBond(value=deposit_amount)
    deploy_client.wait_for_transaction(txn_1_hash)

    assert scheduler.getBondBalance(deploy_coinbase) == deposit_amount

    assert scheduler.isInPool(deploy_coinbase) is False
    assert scheduler.canEnterPool(deploy_coinbase) is True
    deploy_client.wait_for_transaction(scheduler.enterPool())

    txn_2_hash = scheduler.withdrawBond(deposit_amount)
    deploy_client.wait_for_transaction(txn_2_hash)

    assert scheduler.isInPool(deploy_coinbase) is True

    # Withdrawl of full amount not allowed
    assert scheduler.getBondBalance(deploy_coinbase) == deposit_amount

    # wi
    minimum_bond = scheduler.getMinimumBond()
    txn_3_hash = scheduler.withdrawBond(
        deposit_amount - 2 * minimum_bond,
    )
    deploy_client.wait_for_transaction(txn_3_hash)

    # Withdrawl of amount above minimum bond amount is allowed
    assert scheduler.isInPool(deploy_coinbase) is True
    assert scheduler.getBondBalance(deploy_coinbase) == 2 * minimum_bond
