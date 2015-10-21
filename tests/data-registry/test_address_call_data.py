from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "TestDataRegistry",
]


def test_registering_address(deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.TestDataRegistry

    assert client_contract.wasSuccessful.call() == 0

    # This is for a weird bug that I'm not sure how to fix.
    evm = alarm._meta.rpc_client.evm
    evm.mine()

    txn_hash = client_contract.registerAddress.sendTransaction(alarm._meta.address, '0xc948453368e5ddc7bc00bb52b5809138217a068d')
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    assert client_contract.wasSuccessful.call() == 1

    data_hash = alarm.getLastDataHash.call()
    assert data_hash is not None

    data = alarm.getLastData.call()
    assert data == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc9HE3h\xe5\xdd\xc7\xbc\x00\xbbR\xb5\x80\x918!z\x06\x8d'
