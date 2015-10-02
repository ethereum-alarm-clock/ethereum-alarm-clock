from populus.utils import wait_for_transaction


deploy_contracts = [
    "CallerPool",
]


def test_depositing_bond(geth_node, geth_coinbase, deployed_contracts):
    caller_pool = deployed_contracts.CallerPool

    assert caller_pool.callerBonds.call(geth_coinbase) == 0

    txn_1_hash = caller_pool.depositBond.sendTransaction(value=123)
    wait_for_transaction(caller_pool._meta.rpc_client, txn_1_hash)

    assert caller_pool.callerBonds.call(geth_coinbase) == 123

    txn_2_hash = caller_pool.depositBond.sendTransaction(value=456)
    wait_for_transaction(caller_pool._meta.rpc_client, txn_2_hash)

    assert caller_pool.callerBonds.call(geth_coinbase) == 579
