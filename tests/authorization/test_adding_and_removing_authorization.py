from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "AuthorizesOthers",
]


def test_authorizing_other_address(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.AuthorizesOthers
    coinbase = deploy_client.get_coinbase()

    assert alarm.checkAuthorization.call(coinbase, client_contract._meta.address) is False

    wait_for_transaction(deploy_client, client_contract.authorize.sendTransaction(alarm._meta.address))

    assert alarm.checkAuthorization.call(coinbase, client_contract._meta.address) is True

    wait_for_transaction(deploy_client, client_contract.unauthorize.sendTransaction(alarm._meta.address))

    assert alarm.checkAuthorization.call(coinbase, client_contract._meta.address) is False
