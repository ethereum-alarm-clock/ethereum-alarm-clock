from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "NoArgs",
]


def test_getting_target_block(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.NoArgs

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(deploy_client, txn_hash)
    txn = deploy_client.get_transaction_by_hash(txn_hash)

    created_at_block = int(txn['blockNumber'], 16)

    call_key = alarm.getLastCallKey()
    assert call_key is not None

    assert alarm.getCallTargetBlock(call_key) == created_at_block + 40
