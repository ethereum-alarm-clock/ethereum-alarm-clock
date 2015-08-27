deploy_max_wait = 10
deploy_max_retries = 3


def test_check_if_call_successful_for_failed_call(geth_node, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.Fails

    client_contract.scheduleIt.sendTransaction(alarm._meta.address)

    assert client_contract.value.call() is False

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    assert alarm.checkIfCalled.call(callKey) is False
    assert alarm.checkIfSuccess.call(callKey) is False

    alarm.doCall.sendTransaction(callKey)

    assert client_contract.value.call() is True
    assert alarm.checkIfCalled.call(callKey) is True
    assert alarm.checkIfSuccess.call(callKey) is False
