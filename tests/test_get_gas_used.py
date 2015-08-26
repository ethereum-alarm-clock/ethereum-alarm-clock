def test_getting_gas_used(deployed_contracts, eth_coinbase):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.NoArgs

    alarm.client.defaults['from'] = eth_coinbase
    client_contract.client.defaults['from'] = eth_coinbase

    client_contract.scheduleIt.sendTransaction(alarm.address)

    assert client_contract.value.call() is False

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    assert alarm.getCallGasUsed.call(callKey) == 0

    alarm.doCall.sendTransaction(callKey)

    assert client_contract.value.call() is True
    assert alarm.getCallGasUsed.call(callKey) > 10000
