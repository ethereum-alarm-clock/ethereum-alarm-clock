from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "Grove",
    "AuthorizesOthers",
]


def test_authorizing_other_address(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.AuthorizesOthers

    assert alarm.checkAuthorization.call(geth_coinbase, client_contract._meta.address) is False

    wait_for_transaction(rpc_client, client_contract.authorize.sendTransaction(alarm._meta.address))

    assert alarm.checkAuthorization.call(geth_coinbase, client_contract._meta.address) is True

    wait_for_transaction(rpc_client, client_contract.unauthorize.sendTransaction(alarm._meta.address))

    assert alarm.checkAuthorization.call(geth_coinbase, client_contract._meta.address) is False
