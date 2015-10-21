from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "CancelsCall",
]


def test_cancelling_a_call(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.CancelsCall

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(deploy_client, txn_hash)

    call_key = alarm.getLastCallKey()
    assert call_key is not None

    assert alarm.checkIfCancelled(call_key) is False

    cancel_txn_hash = client_contract.cancelIt.sendTransaction(alarm._meta.address, call_key)
    wait_for_transaction(deploy_client, cancel_txn_hash)

    assert alarm.checkIfCancelled(call_key) is True
