import pytest

from populus.contracts import get_max_gas

from eth_alarm_client import (
    Scheduler,
    PoolManager,
    BlockSage,
)


deploy_contracts = [
    "Scheduler",
    "TestCallExecution",
]


@pytest.fixture(autouse=True)
def logging_config(monkeypatch):
    # Set to DEBUG for a better idea of what is going on in this test.
    monkeypatch.setenv('LOG_LEVEL', 'ERROR')


def test_scheduler(geth_node, geth_node_config, deploy_client, deployed_contracts, contracts,
                   get_call, denoms):
    block_sage = BlockSage(deploy_client)

    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.SpecifyBlock

    anchor_block = deploy_client.get_block_number()

    blocks = (1, 4, 4, 8, 30, 40, 50, 60)

    calls = []

    for n in blocks:
        scheduling_txn = scheduler.scheduleCall(
            client_contract._meta.address,
            client_contract.setBool.encoded_abi_signature,
            anchor_block + 100 + n,
            1000000,
            value=10 * denoms.ether,
            gas=3000000,
        )
        scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn)
        call = get_call(scheduling_txn)

        calls.append(call)

    pool_manager = PoolManager(scheduler, block_sage)
    scheduler = Scheduler(scheduler, pool_manager, block_sage=block_sage)
    scheduler.monitor_async()

    final_block = anchor_block + 100 + 70
    wait_for_block(
        deploy_client,
        final_block,
        2 * block_sage.estimated_time_to_block(final_block),
    )

    scheduler.stop()
    block_sage.stop()

    results = [not deploy_client.get_code(call._meta.address) for call in calls]
    assert all(results)
