from populus.utils import wait_for_transaction


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_withdrawing_funds(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    block_reward = 5000000000000000000

    assert alarm.accountBalances.call(geth_coinbase) == 0

    txn_1_hash = alarm.deposit.sendTransaction(geth_coinbase, value=1000)
    txn_1_receipt = wait_for_transaction(rpc_client, txn_1_hash)
    txn_1 = rpc_client.get_transaction_by_hash(txn_1_hash)

    txn_1_gas_cost = int(txn_1['gasPrice'], 16) * int(txn_1_receipt['gasUsed'], 16)

    expected_balance = rpc_client.get_balance(geth_coinbase, int(txn_1['blockNumber'], 16) - 1) - 1000 - txn_1_gas_cost + block_reward
    assert rpc_client.get_balance(geth_coinbase, txn_1['blockNumber']) == expected_balance

    assert alarm.accountBalances.call(geth_coinbase) == 1000

    wait_for_transaction(rpc_client, alarm.withdraw.sendTransaction(250))

    expected_balance += 250
    assert rpc_client.get_balance(geth_coinbase) == expected_balance

    assert alarm.accountBalances.call(geth_coinbase) == 750

    wait_for_transaction(rpc_client, alarm.withdraw.sendTransaction(500))

    expected_balance += 500
    assert rpc_client.get_balance(geth_coinbase) == expected_balance

    assert alarm.accountBalances.call(geth_coinbase) == 250
