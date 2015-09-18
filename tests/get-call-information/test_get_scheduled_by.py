from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_get_scheduled_by(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.NoArgs

    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(rpc_client, txn_hash)

    call_key = alarm.getLastCallKey.call()
    assert call_key

    alarm.getCallScheduledBy.call(call_key) == geth_coinbase
