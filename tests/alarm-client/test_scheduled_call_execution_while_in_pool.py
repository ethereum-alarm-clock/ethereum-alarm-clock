import pytest
import time

from eth_alarm_client import (
    PoolManager,
    ScheduledCall,
    BlockSage,
)


deploy_contracts = [
    "Scheduler",
    "JoinsPool",
    "TestCallExecution",
]


@pytest.fixture(autouse=True)
def scheduler_client_logging_config(monkeypatch):
    # Set to DEBUG for a better idea of what is going on in this test.
    monkeypatch.setenv('LOG_LEVEL', 'ERROR')


def test_scheduled_call_execution_with_pool(geth_node, geth_node_config,
                                            deploy_client, deployed_contracts,
                                            contracts, deploy_coinbase,
                                            get_call, denoms, get_execution_data):
    scheduler = deployed_contracts.Scheduler
    joiner = deployed_contracts.JoinsPool
    client_contract = deployed_contracts.TestCallExecution

    block_sage = BlockSage(deploy_client)

    # Let the block sage spin up.
    time.sleep(4)

    join_txn_hash = joiner.setCallerPool(scheduler._meta.address)
    deploy_client.wait_for_transaction(join_txn_hash)

    assert scheduler.getBondBalance(deploy_coinbase) == 0
    bond_amount = scheduler.getMinimumBond() * 10
    # Put in our bond
    deploy_client.wait_for_transaction(
        scheduler.depositBond(value=bond_amount)
    )

    # Put the contract's bond in
    deploy_client.wait_for_transaction(
        deploy_client.send_transaction(to=joiner._meta.address, value=bond_amount)
    )
    deploy_client.wait_for_transaction(
        joiner.deposit(bond_amount)
    )

    # Both join the pool
    deploy_client.wait_for_transaction(joiner.enter())
    deploy_client.wait_for_transaction(scheduler.enterPool())

    # New pool is formed but not active
    first_generation_id = scheduler.getNextGenerationId()
    assert first_generation_id > 0

    # Go ahead and schedule the call.
    generation_start_at = scheduler.getGenerationStartAt(first_generation_id)
    target_block = generation_start_at + 5

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

    # Wait for the pool to become active
    deploy_client.wait_for_block(
        generation_start_at,
        2 * block_sage.estimated_time_to_block(generation_start_at),
    )

    # We should both be in the pool
    assert scheduler.getCurrentGenerationId() == first_generation_id
    assert scheduler.isInGeneration(joiner._meta.address, first_generation_id) is True
    assert scheduler.isInGeneration(deploy_coinbase, first_generation_id) is True

    scheduled_call = ScheduledCall(scheduler, call_address, block_sage=block_sage)
    pool_manager = PoolManager(scheduler, block_sage=block_sage)

    scheduled_call.execute_async()

    assert scheduled_call.has_been_suicided is False

    deploy_client.wait_for_block(
        scheduled_call.target_block,
        2 * block_sage.estimated_time_to_block(scheduled_call.target_block),
    )

    for i in range(scheduler.getCallWindowSize() * 2):
        if scheduled_call.txn_hash:
            break
        time.sleep(block_sage.block_time)

    assert scheduled_call.txn_hash
    assert scheduled_call.txn_receipt
    assert scheduled_call.txn

    execute_data = get_execution_data(scheduled_call.txn_hash)
    assert execute_data['success'] is True

    assert scheduled_call.has_been_suicided is True
