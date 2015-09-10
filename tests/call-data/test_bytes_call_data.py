from populus.utils import wait_for_transaction


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_registering_bytes(geth_node, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.TestDataRegistry

    assert client_contract.wasSuccessful.call() == 0

    txn_hash = client_contract.registerBytes.sendTransaction(alarm._meta.address, 'abcd')
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    assert client_contract.wasSuccessful.call() == 1

    data_hash = alarm.getLastDataHash.call()
    assert data_hash is not None

    data = alarm.getLastData.call()
    assert data == 'abcd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
