from populus.utils import wait_for_transaction


def test_depositing_funds_with_fallback_function(geth_node, geth_coinbase, deployed_contracts):
    alarm = deployed_contracts.Alarm

    assert alarm.getAccountBalance.call(geth_coinbase) == 0

    txn_1_hash = alarm._meta.rpc_client.send_transaction(
        to=alarm._meta.address,
        data="notavalidfunctioncall",
        value=123,
    )
    wait_for_transaction(alarm._meta.rpc_client, txn_1_hash)

    assert alarm.getAccountBalance.call(geth_coinbase) == 123

    txn_2_hash = alarm._meta.rpc_client.send_transaction(
        to=alarm._meta.address,
        data="notavalidfunctioncall",
        value=456,
    )
    wait_for_transaction(alarm._meta.rpc_client, txn_2_hash)

    assert alarm.getAccountBalance.call(geth_coinbase) == 579
