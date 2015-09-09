def test_executing_scheduled_call(geth_node, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.PassesUInt

    client_contract.scheduleIt.sendTransaction(alarm.address, 3)

    assert client_contract.value.call() == 0

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None
    alarm.doCall.sendTransaction(callKey)

    assert client_contract.value.call() == 3
    call_data = alarm.getCallData.call(callKey)
    assert call_data == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03'
