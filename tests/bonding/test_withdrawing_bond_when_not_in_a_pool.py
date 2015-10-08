from ethereum.utils import denoms

from populus.utils import wait_for_transaction


deploy_contracts = [
    "CallerPool",
]


def get_balance_delta(rpc_client, txn_hash):
    coinbase = rpc_client.get_coinbase()
    txn = rpc_client.get_transaction_by_hash(txn_hash)
    before_txn_balance = rpc_client.get_balance(coinbase, int(txn['blockNumber'], 16) - 1)
    after_txn_balance = rpc_client.get_balance(coinbase, txn['blockNumber'])

    delta = before_txn_balance - after_txn_balance
    return delta


def test_withdrawing_bond_while_not_in_a_pool(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    caller_pool = deployed_contracts.CallerPool
    block_reward = 5000000000000000000

    assert caller_pool.callerBonds.call(geth_coinbase) == 0

    txn_1_hash = caller_pool.depositBond.sendTransaction(value=1000 * denoms.ether)
    wait_for_transaction(rpc_client, txn_1_hash)

    txn_1_delta = get_balance_delta(rpc_client, txn_1_hash)

    assert txn_1_delta == 1000 * denoms.ether - block_reward
    assert caller_pool.callerBonds.call(geth_coinbase) == 1000 * denoms.ether

    txn_2_hash = caller_pool.withdrawBond.sendTransaction(250 * denoms.ether)
    wait_for_transaction(rpc_client, txn_2_hash)

    txn_2_delta = get_balance_delta(rpc_client, txn_2_hash)

    assert txn_2_delta == -1 * 250 * denoms.ether - block_reward

    assert caller_pool.callerBonds.call(geth_coinbase) == 750 * denoms.ether

    txn_3_hash = caller_pool.withdrawBond.sendTransaction(500 * denoms.ether)
    wait_for_transaction(rpc_client, txn_3_hash)

    txn_3_delta = get_balance_delta(rpc_client, txn_3_hash)

    assert txn_3_delta == -1 * 500 * denoms.ether - block_reward

    assert caller_pool.callerBonds.call(geth_coinbase) == 250 * denoms.ether
