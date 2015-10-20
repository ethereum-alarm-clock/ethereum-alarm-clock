from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "PassesInt",
]


def test_extra_call_gas_constant_when_gas_price_lower(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.PassesInt

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, -12345)
    wait_for_transaction(deploy_client, txn_hash)

    call_key = alarm.getLastCallKey()
    assert call_key is not None

    base_gas_price = alarm.getCallBaseGasPrice(call_key)

    deploy_client.mine_until_block(alarm.getCallTargetBlock(call_key))
    call_txn_hash = alarm.doCall.sendTransaction(call_key)

    call_txn_receipt = wait_for_transaction(deploy_client, call_txn_hash)

    assert alarm.checkIfCalled(call_key) is True

    recorded_gas_used = alarm.getCallGasUsed(call_key)
    actual_gas_used = int(call_txn_receipt['gasUsed'], 16)

    try:
        assert actual_gas_used == recorded_gas_used
    except AssertionError:
        assert actual_gas_used == recorded_gas_used + 44
