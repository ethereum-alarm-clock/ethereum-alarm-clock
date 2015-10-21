from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "TestDataRegistry",
]


def test_registering_int(deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.TestDataRegistry


    assert client_contract.wasSuccessful() == 0

    # This is for a weird bug that I'm not sure how to fix.
    evm = alarm._meta.rpc_client.evm
    evm.mine()

    txn_hash = client_contract.registerInt.sendTransaction(alarm._meta.address, 3)
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    assert client_contract.wasSuccessful() == 1

    data_hash = alarm.getLastDataHash()
    assert data_hash is not None

    data = alarm.getLastData.call()
    assert data == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03'
