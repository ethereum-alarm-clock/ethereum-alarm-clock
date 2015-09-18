from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction, wait_for_block

deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_extra_call_gas_constant_when_gas_price_higher(geth_node, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.PassesInt

    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, -12345)
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    base_gas_price = alarm.getCallBaseGasPrice.call(callKey)

    wait_for_block(rpc_client, alarm.getCallTargetBlock.call(callKey), 120)
    call_txn_hash = alarm.doCall.sendTransaction(callKey, gas_price=base_gas_price + 10)

    call_txn_receipt = wait_for_transaction(alarm._meta.rpc_client, call_txn_hash)

    assert alarm.checkIfCalled.call(callKey) is True

    recorded_gas_used = alarm.getCallGasUsed.call(callKey)
    actual_gas_used = int(call_txn_receipt['gasUsed'], 16)

    assert actual_gas_used == recorded_gas_used
