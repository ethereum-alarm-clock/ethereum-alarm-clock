def test_get_call_gas_cost(deployed_contracts, eth_coinbase):
    alarm = deployed_contracts.Alarm
    trigger = deployed_contracts.Trigger

    alarm.client.defaults['from'] = eth_coinbase
    trigger.client.defaults['from'] = eth_coinbase

    trigger.scheduleIt.sendTransaction(alarm.address[2:], 3)

    assert trigger.value.call() == 0

    callHash = alarm.getLastCallHash.call()
    assert callHash is not None
    alarm.doCall.sendTransaction(callHash)

    assert trigger.value.call() == 3

    gas_before = alarm.getGasBefore.call(callHash)
    gas_after = alarm.getGasAfter.call(callHash)

    import ipdb; ipdb.set_trace()
    x = 3
