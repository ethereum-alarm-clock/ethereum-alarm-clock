from ethereum import utils as ethereum_utils


def test_executing_scheduled_call(deployed_contracts, eth_coinbase):
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


def test_get_call_value(deployed_contracts, eth_coinbase):
    alarm = deployed_contracts.Alarm
    alarm.client.defaults['from'] = eth_coinbase

    alarm.scheduleCall.sendTransaction('arst', ethereum_utils.decode_hex('c3305bc9de1244e48050962ced50b75934c37006e99e8b7a62213e945c3dfcd7'), 1000, value=12345)
    last_call_hash = alarm.getLastCallHash.call()
    assert last_call_hash

    value = alarm.getCallValue.call(last_call_hash)
    assert value == 12345
