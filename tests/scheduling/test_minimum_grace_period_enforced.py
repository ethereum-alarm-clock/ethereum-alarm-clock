from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "Grove",
    "NoArgs",
]


def test_minimum_grace_period_enforced(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.NoArgs

    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    wait_for_transaction(rpc_client, client_contract.setGracePeriod.sendTransaction(8))
    txn_1_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(rpc_client, txn_1_hash)

    call_key = alarm.getLastCallKey.call()
    assert call_key is None

    wait_for_transaction(rpc_client, client_contract.setGracePeriod.sendTransaction(16))
    txn_2_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(rpc_client, txn_2_hash)

    call_key = alarm.getLastCallKey.call()
    assert call_key is not None

    alarm.getCallGracePeriod.call(call_key) == 16
