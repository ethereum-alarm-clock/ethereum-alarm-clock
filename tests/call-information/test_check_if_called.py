from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "NoArgs",
]


def test_check_if_called(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.NoArgs

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(deploy_client, txn_hash)

    assert client_contract.value() is False

    call_key = alarm.getLastCallKey()
    assert call_key is not None

    assert alarm.checkIfCalled(call_key) is False

    deploy_client.wait_for_block(alarm.getCallTargetBlock(call_key))
    call_txn_hash = alarm.doCall.sendTransaction(call_key)
    wait_for_transaction(alarm._meta.rpc_client, call_txn_hash)

    assert client_contract.value() is True
    assert alarm.checkIfCalled(call_key) is True
