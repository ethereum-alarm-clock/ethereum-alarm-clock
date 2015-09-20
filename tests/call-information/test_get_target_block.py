from populus.utils import wait_for_transaction


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_getting_target_block(geth_node, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.NoArgs

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)
    txn = client_contract._meta.rpc_client.get_transaction_by_hash(txn_hash)

    created_at_block = int(txn['blockNumber'], 16)

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    assert alarm.getCallTargetBlock.call(callKey) == created_at_block + 40
