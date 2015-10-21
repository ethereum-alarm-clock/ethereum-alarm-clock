import pytest
import time
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
    "SpecifyBlock",
]


@pytest.fixture(autouse=True)
def alarm_client_logging_config(monkeypatch):
    # Set to DEBUG for a better idea of what is going on in this test.
    monkeypatch.setenv('LOG_LEVEL', 'ERROR')


def test_scheduled_call_execution_without_pool(geth_node, geth_node_config, deploy_client, deployed_contracts, contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.SpecifyBlock

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    target_block = deploy_client.get_block_number() + 45

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, target_block)
    wait_for_transaction(deploy_client, txn_hash)

    call_key = alarm.getLastCallKey()
    assert call_key is not None

    scheduled_call = ScheduledCall(alarm, call_key)
    block_sage = scheduled_call.block_sage
    pool_manager = PoolManager(alarm, block_sage=block_sage)

    time.sleep(1)

    assert pool_manager.in_any_pool is False
    scheduled_call.execute_async()

    # let the scheduled call do it's thing.
    assert block_sage.current_block_number < target_block

    wait_till = scheduled_call.target_block + 10
    wait_for_block(
        deploy_client,
        wait_till,
        2 * block_sage.estimated_time_to_block(wait_till),
    )

    for i in range(5):
        if scheduled_call.txn_hash:
            break
        time.sleep(block_sage.block_time)

    assert scheduled_call.txn_hash
    assert scheduled_call.txn_receipt
    assert scheduled_call.txn

    assert alarm.checkIfCalled(scheduled_call.call_key)
    assert scheduled_call.was_called
    assert scheduled_call.target_block <= scheduled_call.called_at_block
    assert scheduled_call.called_at_block <= scheduled_call.target_block + scheduled_call.grace_period
