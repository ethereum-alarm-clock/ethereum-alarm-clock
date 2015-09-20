from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_cannot_schedule_too_soon(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.SpecifyBlock

    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleDelta.sendTransaction(alarm._meta.address, 39)
    wait_for_transaction(rpc_client, txn_hash)

    call_key = alarm.getLastCallKey.call()
    assert call_key is None

    txn_hash = client_contract.scheduleDelta.sendTransaction(alarm._meta.address, 40)
    wait_for_transaction(rpc_client, txn_hash)

    call_key = alarm.getLastCallKey.call()
    assert call_key is not None
