from ethereum.utils import denoms

from populus.utils import wait_for_transaction


deploy_max_wait = 30
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def get_balance_delta(rpc_client, txn_hash):
    coinbase = rpc_client.get_coinbase()
    txn = rpc_client.get_transaction_by_hash(txn_hash)
    before_txn_balance = rpc_client.get_balance(coinbase, int(txn['blockNumber'], 16) - 1)
    after_txn_balance = rpc_client.get_balance(coinbase, txn['blockNumber'])

    delta = before_txn_balance - after_txn_balance
    return delta


def test_withdrawing_bond_denied_when_in_pool(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    caller_pool = deployed_contracts.CallerPool
    block_reward = 5000000000000000000

    assert caller_pool.callerBonds.call(geth_coinbase) == 0
    deposit_amount = caller_pool.getMinimumBond.call() * 10

    txn_1_hash = caller_pool.depositBond.sendTransaction(value=deposit_amount)
    wait_for_transaction(rpc_client, txn_1_hash)

    txn_1_delta = get_balance_delta(rpc_client, txn_1_hash)

    assert txn_1_delta == deposit_amount - block_reward
    assert caller_pool.callerBonds.call(geth_coinbase) == deposit_amount

    assert caller_pool.isInAnyPool.call() is False
    assert caller_pool.canEnterPool.call() is True
    wait_for_transaction(rpc_client, caller_pool.enterPool.sendTransaction())

    txn_2_hash = caller_pool.withdrawBond.sendTransaction(250 * denoms.ether)
    wait_for_transaction(rpc_client, txn_2_hash)

    txn_2_delta = get_balance_delta(rpc_client, txn_2_hash)

    assert txn_2_delta == -1 * block_reward
    assert caller_pool.isInAnyPool.call() is True
    assert caller_pool.canEnterPool.call() is False
