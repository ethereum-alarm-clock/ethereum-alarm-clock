from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "NoArgs",
]


def test_getting_gas_used(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.NoArgs

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(deploy_client, txn_hash)

    assert client_contract.value() is False

    call_key = alarm.getLastCallKey()
    assert call_key is not None

    assert alarm.getCallGasUsed(call_key) == 0

    deploy_client.wait_for_block(alarm.getCallTargetBlock(call_key), 120)
    call_txn_hash = alarm.doCall.sendTransaction(call_key)
    call_txn_receipt = wait_for_transaction(deploy_client, call_txn_hash)

    assert client_contract.value() is True
    recorded_gas =  alarm.getCallGasUsed(call_key)
    actual_gas = int(call_txn_receipt['gasUsed'], 16)
    assert recorded_gas >= actual_gas
    assert abs(recorded_gas - actual_gas) < 100
