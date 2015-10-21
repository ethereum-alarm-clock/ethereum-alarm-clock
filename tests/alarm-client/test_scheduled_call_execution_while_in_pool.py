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
    BlockSage,
)


deploy_contracts = [
    "Alarm",
    "JoinsPool",
    "SpecifyBlock",
]


@pytest.fixture(autouse=True)
def alarm_client_logging_config(monkeypatch):
    # Set to DEBUG for a better idea of what is going on in this test.
    monkeypatch.setenv('LOG_LEVEL', 'ERROR')


def test_scheduled_call_execution_with_pool(geth_node, geth_coinbase, geth_node_config, deploy_client, deployed_contracts, contracts):
    alarm = deployed_contracts.Alarm
    joiner = deployed_contracts.JoinsPool
    client_contract = deployed_contracts.SpecifyBlock

    coinbase = geth_coinbase

    block_sage = BlockSage(deploy_client)

    # Put in our deposit with the alarm contract.
    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    wait_for_transaction(deploy_client, joiner.setCallerPool.sendTransaction(alarm._meta.address))

    assert alarm.getBondBalance(coinbase) == 0
    bond_amount = alarm.getMinimumBond() * 10
    # Put in our bond
    wait_for_transaction(
        deploy_client, alarm.depositBond.sendTransaction(value=bond_amount)
    )

    # Put the contract's bond in
    wait_for_transaction(
        deploy_client,
        deploy_client.send_transaction(to=joiner._meta.address, value=bond_amount)
    )
    wait_for_transaction(
        deploy_client, joiner.deposit.sendTransaction(bond_amount)
    )

    # Both join the pool
    wait_for_transaction(deploy_client, joiner.enter.sendTransaction())
    wait_for_transaction(deploy_client, alarm.enterPool.sendTransaction())

    # New pool is formed but not active
    first_generation_id = alarm.getNextGenerationId()
    assert first_generation_id > 0

    # Go ahead and schedule the call.
    generation_start_at = alarm.getGenerationStartAt(first_generation_id)
    target_block = generation_start_at + 5

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, target_block)
    wait_for_transaction(deploy_client, txn_hash)

    # Wait for the pool to become active
    wait_for_block(
        deploy_client,
        generation_start_at,
        2 * block_sage.estimated_time_to_block(generation_start_at),
    )

    # We should both be in the pool
    assert alarm.getCurrentGenerationId() == first_generation_id
    assert alarm.isInGeneration(joiner._meta.address, first_generation_id) is True
    assert alarm.isInGeneration(coinbase, first_generation_id) is True

    call_key = alarm.getLastCallKey()
    assert call_key is not None

    scheduled_call = ScheduledCall(alarm, call_key, block_sage=block_sage)
    pool_manager = PoolManager(alarm, block_sage=block_sage)

    scheduled_call.execute_async()

    wait_for_block(
        deploy_client,
        scheduled_call.target_block,
        2 * block_sage.estimated_time_to_block(scheduled_call.target_block),
    )

    for i in range(alarm.getCallWindowSize() * 2):
        if scheduled_call.txn_hash:
            break
        time.sleep(block_sage.block_time)

    assert scheduled_call.txn_hash
    assert scheduled_call.txn_receipt
    assert scheduled_call.txn

    assert scheduled_call.was_called
    assert alarm.checkIfCalled(scheduled_call.call_key)
    assert scheduled_call.target_block <= scheduled_call.called_at_block
    assert scheduled_call.called_at_block <= scheduled_call.target_block + scheduled_call.grace_period
