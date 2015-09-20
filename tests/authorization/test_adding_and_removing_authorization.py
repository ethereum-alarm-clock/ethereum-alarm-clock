from populus.utils import wait_for_transaction


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_authorizing_other_address(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.AuthorizesOthers

    assert alarm.checkAuthorization.call(geth_coinbase, client_contract._meta.address) is False

    wait_for_transaction(rpc_client, client_contract.authorize.sendTransaction(alarm._meta.address))

    assert alarm.checkAuthorization.call(geth_coinbase, client_contract._meta.address) is True

    wait_for_transaction(rpc_client, client_contract.unauthorize.sendTransaction(alarm._meta.address))

    assert alarm.checkAuthorization.call(geth_coinbase, client_contract._meta.address) is False
