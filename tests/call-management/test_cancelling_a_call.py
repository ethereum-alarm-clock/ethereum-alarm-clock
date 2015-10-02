from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "Grove",
    "CancelsCall",
]


def test_cancelling_a_call(geth_node, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.CancelsCall

    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    assert alarm.checkIfCancelled.call(callKey) is False

    wait_for_transaction(rpc_client, client_contract.cancelIt.sendTransaction(alarm._meta.address, callKey))

    assert alarm.checkIfCancelled.call(callKey) is True
