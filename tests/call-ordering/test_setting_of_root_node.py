from populus.utils import wait_for_transaction


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_first_call_registered_is_set_as_root(geth_node, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.SpecifyBlock

    assert alarm.rootNodeCallKey.call(raw=True) == "0x0000000000000000000000000000000000000000000000000000000000000000"

    current_block = rpc_client.get_block_number()

    wait_for_transaction(rpc_client, client_contract.scheduleIt.sendTransaction(alarm._meta.address, current_block + 100))

    last_call_key = alarm.getLastCallKey.call()
    assert last_call_key is not None

    assert alarm.rootNodeCallKey.call() == last_call_key
