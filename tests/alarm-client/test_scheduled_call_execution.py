from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction

from alarm_client.client import ScheduledCall


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_scheduled_call_execution(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.SpecifyBlock

    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    target_block = rpc_client.get_block_number() + 45

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, target_block)
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    scheduled_call = ScheduledCall(alarm, callKey)

    scheduled_call.execute()

    assert scheduled_call.txn_hash
    assert scheduled_call.txn_receipt
    assert scheduled_call.txn

    assert scheduled_call.was_called
    assert scheduled_call.target_block <= scheduled_call.called_at_block
    assert scheduled_call.called_at_block <= scheduled_call.target_block + scheduled_call.grace_period
