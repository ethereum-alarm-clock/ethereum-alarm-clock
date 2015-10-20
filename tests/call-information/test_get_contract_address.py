from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "NoArgs",
]


def test_getting_contract_address(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.NoArgs

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(deploy_client, txn_hash)

    assert client_contract.value() is False

    call_key = alarm.getLastCallKey()
    assert call_key is not None

    assert alarm.getCallContractAddress(call_key) == client_contract._meta.address
