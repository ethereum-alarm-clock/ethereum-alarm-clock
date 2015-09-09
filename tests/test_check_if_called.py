deploy_max_wait = 15
deploy_max_first_block_wait = 180
geth_max_wait = 45


def test_check_if_called(geth_node, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.NoArgs

    client_contract.scheduleIt.sendTransaction(alarm._meta.address)

    assert client_contract.value.call() is False

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    assert alarm.checkIfCalled.call(callKey) is False

    alarm.doCall.sendTransaction(callKey)

    assert client_contract.value.call() is True
    assert alarm.checkIfCalled.call(callKey) is True
