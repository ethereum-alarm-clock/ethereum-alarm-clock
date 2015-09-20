from populus.utils import wait_for_transaction


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_registering_using_local_abstraction(geth_node, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.TestDataRegistry

    assert client_contract.wasSuccessful.call() == 0

    txn_hash = client_contract.registerData.sendTransaction(
        alarm._meta.address,
        -1 * (2 ** 128 - 1),
        '1234567890\00\00\00abcdefg',
        '0xc948453368e5ddc7bc00bb52b5809138217a068d',
    )

    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    assert client_contract.wasSuccessful.call() == 1

    data_hash = alarm.getLastDataHash.call()
    assert data_hash is not None

    data = alarm.getLastData.call()
    assert data == (
        '\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'
        '1234567890\x00\x00\x00abcdefg\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc9HE3h\xe5\xdd\xc7\xbc\x00\xbbR\xb5\x80\x918!z\x06\x8d'
    )
