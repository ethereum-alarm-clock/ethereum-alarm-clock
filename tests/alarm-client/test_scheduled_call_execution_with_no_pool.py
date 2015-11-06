import pytest
import time

from eth_alarm_client import (
    PoolManager,
    ScheduledCall,
)


deploy_contracts = [
    "Scheduler",
    "TestCallExecution",
]


@pytest.fixture(autouse=True)
def scheduler_client_logging_config(monkeypatch):
    # Set to DEBUG for a better idea of what is going on in this test.
    monkeypatch.setenv('LOG_LEVEL', 'ERROR')


def test_scheduled_call_execution_without_pool(geth_node, geth_node_config,
                                               deploy_client,
                                               deployed_contracts, contracts,
                                               denoms, get_call, get_execution_data):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    target_block = deploy_client.get_block_number() + 45

    scheduling_txn = scheduler.scheduleCall(
        client_contract._meta.address,
        client_contract.setBool.encoded_abi_signature,
        target_block,
        1000000,
        value=10 * denoms.ether,
        gas=3000000,
    )
    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn)
    call = get_call(scheduling_txn)
    call_address = call._meta.address

    scheduled_call = ScheduledCall(scheduler, call_address)
    block_sage = scheduled_call.block_sage
    pool_manager = PoolManager(scheduler, block_sage=block_sage)

    time.sleep(1)

    assert pool_manager.in_any_pool is False
    scheduled_call.execute_async()

    # let the scheduled call do it's thing.
    assert block_sage.current_block_number < target_block
    assert scheduled_call.has_been_suicided is False

    wait_till = scheduled_call.target_block + 10
    deploy_client.wait_for_block(
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

    execute_data = get_execution_data(scheduled_call.txn_hash)
    assert execute_data['success'] is True

    assert scheduled_call.has_been_suicided is True
