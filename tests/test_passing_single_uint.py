deploy_max_wait = 15
deploy_max_first_block_wait = 180

geth_max_wait = 45


def test_executing_scheduled_call_with_uint(geth_node, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.PassesUInt

    client_contract.scheduleIt.sendTransaction(alarm._meta.address, 3)

    assert client_contract.value.call() == 0

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None
    alarm.doCall.sendTransaction(callKey)

    assert client_contract.value.call() == 3
