from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "SpecifyBlock",
]


def test_cannot_schedule_too_soon(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.SpecifyBlock

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleDelta.sendTransaction(alarm._meta.address, 39)
    wait_for_transaction(deploy_client, txn_hash)

    call_key = alarm.getLastCallKey()
    assert call_key is None

    txn_hash = client_contract.scheduleDelta.sendTransaction(alarm._meta.address, 40)
    wait_for_transaction(deploy_client, txn_hash)

    call_key = alarm.getLastCallKey()
    assert call_key is not None
