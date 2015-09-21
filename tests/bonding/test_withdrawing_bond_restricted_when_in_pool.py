from ethereum.utils import denoms

from populus.utils import wait_for_transaction


deploy_max_wait = 30
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_withdrawing_bond_restricted_when_in_pool(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    caller_pool = deployed_contracts.CallerPool

    assert caller_pool.callerBonds.call(geth_coinbase) == 0
    deposit_amount = caller_pool.getMinimumBond.call() * 10

    txn_1_hash = caller_pool.depositBond.sendTransaction(value=deposit_amount)
    wait_for_transaction(rpc_client, txn_1_hash)

    assert caller_pool.callerBonds.call(geth_coinbase) == deposit_amount

    assert caller_pool.isInAnyPool.call(geth_coinbase) is False
    assert caller_pool.canEnterPool.call(geth_coinbase) is True
    wait_for_transaction(rpc_client, caller_pool.enterPool.sendTransaction())

    txn_2_hash = caller_pool.withdrawBond.sendTransaction(deposit_amount)
    wait_for_transaction(rpc_client, txn_2_hash)

    assert caller_pool.isInAnyPool.call(geth_coinbase) is True

    # Withdrawl of full amount not allowed
    assert caller_pool.callerBonds.call(geth_coinbase) == deposit_amount

    # wi
    minimum_bond = caller_pool.getMinimumBond.call()
    txn_3_hash = caller_pool.withdrawBond.sendTransaction(
        deposit_amount - 2 * minimum_bond,
    )
    wait_for_transaction(rpc_client, txn_3_hash)

    # Withdrawl of amount above minimum bond amount is allowed
    assert caller_pool.isInAnyPool.call(geth_coinbase) is True
    assert caller_pool.callerBonds.call(geth_coinbase) == 2 * minimum_bond
