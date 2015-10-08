from populus.utils import wait_for_transaction


def test_withdrawing_with_insufficient_funds(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm

    assert alarm.accountBalances.call(geth_coinbase) == 0

    wait_for_transaction(rpc_client, alarm.deposit.sendTransaction(geth_coinbase, value=1000))

    assert alarm.accountBalances.call(geth_coinbase) == 1000

    wait_for_transaction(rpc_client, alarm.withdraw.sendTransaction(1001))

    assert alarm.accountBalances.call(geth_coinbase) == 1000

    wait_for_transaction(rpc_client, alarm.withdraw.sendTransaction(1000))

    assert alarm.accountBalances.call(geth_coinbase) == 0
