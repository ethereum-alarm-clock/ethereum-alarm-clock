from populus.utils import wait_for_transaction


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_getting_called_at_block(geth_node, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.NoArgs

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    assert client_contract.value.call() is False

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    assert alarm.getCallGasUsed.call(callKey) == 0

    call_txn_hash = alarm.doCall.sendTransaction(callKey)
    wait_for_transaction(alarm._meta.rpc_client, call_txn_hash)

    call_txn = alarm._meta.rpc_client.get_transaction_by_hash(call_txn_hash)

    assert client_contract.value.call() is True
    assert alarm.getCallCalledAtBlock.call(callKey) == int(call_txn['blockNumber'], 16)
