from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "PassesBytes32",
]


def test_executing_scheduled_call_with_bytes32(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.PassesBytes32

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, 'abc\x00\x00\x00\x00\x00abc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    wait_for_transaction(deploy_client, txn_hash)

    assert client_contract.value() is None

    call_key = alarm.getLastCallKey()
    assert call_key is not None
    deploy_client.wait_for_block(alarm.getCallTargetBlock(call_key), 120)
    call_txn_hash = alarm.doCall.sendTransaction(call_key)
    wait_for_transaction(deploy_client, call_txn_hash)

    assert client_contract.value() == 'abc\x00\x00\x00\x00\x00abc'
