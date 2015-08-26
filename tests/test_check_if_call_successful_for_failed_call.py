import pytest


@pytest.mark.skipif(True, reason="Doesn't work with test rpc server")
def test_check_if_call_successful_for_failed_call(deployed_contracts, eth_coinbase):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.Fails

    alarm.client.defaults['from'] = eth_coinbase
    client_contract.client.defaults['from'] = eth_coinbase

    client_contract.scheduleIt.sendTransaction(alarm.address)

    assert client_contract.value.call() is False

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    assert alarm.checkIfCalled.call(callKey) is False
    assert alarm.checkIfSuccess.call(callKey) is False

    alarm.doCall.sendTransaction(callKey)

    assert client_contract.value.call() is True
    assert alarm.checkIfCalled.call(callKey) is True
    assert alarm.checkIfSuccess.call(callKey) is False
