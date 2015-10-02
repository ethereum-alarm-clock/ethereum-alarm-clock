from populus.contracts import get_max_gas
from populus.utils import (
    wait_for_transaction,
    wait_for_block,
)

from eth_alarm_client import (
    PoolManager,
    ScheduledCall,
)


deploy_contracts = [
    "Alarm",
    "Grove",
    "SpecifyBlock",
]


def test_scheduled_call_execution_without_pool(geth_node, geth_coinbase, rpc_client, deployed_contracts, contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.SpecifyBlock
    caller_pool = contracts.CallerPool(alarm.getCallerPoolAddress.call(), rpc_client)

    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    target_block = rpc_client.get_block_number() + 45

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, target_block)
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    pool_manager = PoolManager(caller_pool)
    scheduled_call = ScheduledCall(alarm, pool_manager, callKey)

    assert pool_manager.in_active_pool is False
    scheduled_call.execute_async()

    wait_for_block(rpc_client, scheduled_call.target_block + 4, 180)
    assert pool_manager.in_active_pool is False

    assert scheduled_call.txn_hash
    assert scheduled_call.txn_receipt
    assert scheduled_call.txn

    assert alarm.checkIfCalled.call(scheduled_call.call_key)
    assert scheduled_call.was_called
    assert scheduled_call.target_block <= scheduled_call.called_at_block
    assert scheduled_call.called_at_block <= scheduled_call.target_block + scheduled_call.grace_period
