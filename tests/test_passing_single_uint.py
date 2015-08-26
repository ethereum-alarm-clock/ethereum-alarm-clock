def test_executing_scheduled_call(deployed_contracts, eth_coinbase):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.PassesUInt

    alarm.client.defaults['from'] = eth_coinbase
    client_contract.client.defaults['from'] = eth_coinbase

    client_contract.scheduleIt.sendTransaction(alarm.address, 3)

    assert client_contract.value.call() == 0

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None
    alarm.doCall.sendTransaction(callKey)

    assert client_contract.value.call() == 3
