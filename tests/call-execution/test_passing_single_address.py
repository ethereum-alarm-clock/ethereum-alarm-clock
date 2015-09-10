from populus.utils import wait_for_transaction


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_executing_scheduled_call_with_address(geth_node, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.PassesAddress

    address = '0xc948453368e5ddc7bc00bb52b5809138217a068d'

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, address)
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    assert client_contract.value.call() == '0x0000000000000000000000000000000000000000'

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None
    call_txn_hash = alarm.doCall.sendTransaction(callKey)
    wait_for_transaction(alarm._meta.rpc_client, call_txn_hash)

    assert client_contract.value.call() == address
