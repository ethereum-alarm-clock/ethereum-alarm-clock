from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "PassesInt",
]


def test_extra_call_gas_constant_when_gas_price_higher(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.PassesInt

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, -12345)
    wait_for_transaction(deploy_client, txn_hash)

    call_key = alarm.getLastCallKey()
    assert call_key is not None

    base_gas_price = alarm.getCallBaseGasPrice(call_key)

    deploy_client.wait_for_block(alarm.getCallTargetBlock(call_key), 120)
    call_txn_hash = alarm.doCall.sendTransaction(call_key, gas_price=base_gas_price + 10)

    call_txn_receipt = wait_for_transaction(deploy_client, call_txn_hash)

    assert alarm.checkIfCalled(call_key) is True

    recorded_gas_used = alarm.getCallGasUsed(call_key)
    actual_gas_used = int(call_txn_receipt['gasUsed'], 16)

    assert recorded_gas_used >= actual_gas_used

    assert abs(recorded_gas_used - actual_gas_used) in {0, 64}
