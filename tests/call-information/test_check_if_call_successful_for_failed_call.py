from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "InfiniteLoop",
]


def test_check_if_call_successful_for_failed_call(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.InfiniteLoop

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(deploy_client, txn_hash)

    call_key = alarm.getLastCallKey()
    assert call_key is not None

    assert alarm.checkIfCalled(call_key) is False
    assert alarm.checkIfSuccess(call_key) is False

    deploy_client.wait_for_block(alarm.getCallTargetBlock(call_key), 120)
    call_txn_hash = alarm.doCall.sendTransaction(call_key)
    call_txn_receipt = wait_for_transaction(deploy_client, call_txn_hash)
    call_txn = deploy_client.get_transaction_by_hash(call_txn_hash)

    assert alarm.checkIfCalled(call_key) is True
    assert alarm.checkIfSuccess(call_key) is False
    assert int(call_txn_receipt['gasUsed'], 16) == int(call_txn['gas'], 16)
