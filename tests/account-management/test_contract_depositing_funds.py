from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "Grove",
    "DepositsFunds",
]


def test_contract_depositing_funds(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    depositer = deployed_contracts.DepositsFunds

    assert alarm.getAccountBalance.call(depositer._meta.address) == 0

    wait_for_transaction(rpc_client, rpc_client.send_transaction(
        to=depositer._meta.address,
        value=1000000,
    ))

    assert rpc_client.get_balance(depositer._meta.address) == 1000000

    assert depositer.sentSuccessful.call() == 0

    wait_for_transaction(rpc_client, depositer.doIt.sendTransaction(
        alarm._meta.address,
        123,
    ))

    assert depositer.sentSuccessful.call() == 1

    assert alarm.getAccountBalance.call(geth_coinbase) == 0
    assert alarm.getAccountBalance.call(depositer._meta.address) == 123

    wait_for_transaction(rpc_client, depositer.doIt.sendTransaction(
        alarm._meta.address,
        456,
    ))

    assert alarm.getAccountBalance.call(depositer._meta.address) == 579
