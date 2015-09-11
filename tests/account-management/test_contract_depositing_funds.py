from populus.utils import wait_for_transaction


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_contract_depositing_funds(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    depositer = deployed_contracts.DepositsFunds

    assert alarm.accountBalances.call(depositer._meta.address) == 0

    wait_for_transaction(rpc_client, depositer._meta.rpc_client.send_transaction(
        to=depositer._meta.address,
        value=1000,
    ))

    assert depositer.sentSuccessful.call() is False

    wait_for_transaction(rpc_client, depositer.doIt.sendTransaction(
        alarm._meta.address,
        123,
    ))

    assert depositer.sentSuccessful.call() is True

    assert alarm.accountBalances.call(geth_coinbase) == 0
    assert alarm.accountBalances.call(depositer._meta.address) == 123

    wait_for_transaction(rpc_client, depositer.doIt.sendTransaction(
        alarm._meta.address,
        456,
    ))

    assert alarm.accountBalances.call(depositer._meta.address) == 579
