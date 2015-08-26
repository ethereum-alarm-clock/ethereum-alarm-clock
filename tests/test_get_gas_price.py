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

    txn_hash = alarm.doCall.sendTransaction(callKey)
    txn = alarm.client.get_transaction_by_hash(txn_hash)

    assert client_contract.value.call() is True
    assert alarm.getCallGasPrice.call(callKey) == int(txn['gasPrice'], 16)

