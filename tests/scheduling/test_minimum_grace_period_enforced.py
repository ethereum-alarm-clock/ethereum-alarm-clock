from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "NoArgs",
]


def test_minimum_grace_period_enforced(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.NoArgs

    minimum_grace_period = alarm.getMinimumGracePeriod()

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    wait_for_transaction(deploy_client, client_contract.setGracePeriod.sendTransaction(minimum_grace_period - 1))
    txn_1_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(deploy_client, txn_1_hash)

    call_key = alarm.getLastCallKey.call()
    assert call_key is None

    wait_for_transaction(deploy_client, client_contract.setGracePeriod.sendTransaction(minimum_grace_period))
    txn_2_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(deploy_client, txn_2_hash)

    call_key = alarm.getLastCallKey.call()
    assert call_key is not None

    alarm.getCallGracePeriod.call(call_key) == 16
