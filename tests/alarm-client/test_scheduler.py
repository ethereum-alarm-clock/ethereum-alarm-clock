import pytest

from populus.contracts import get_max_gas
from populus.utils import (
    wait_for_transaction,
    wait_for_block,
)

from eth_alarm_client import (
    Scheduler,
    PoolManager,
    BlockSage,
)


deploy_contracts = [
    "Alarm",
    "SpecifyBlock",
]


@pytest.fixture(autouse=True)
def alarm_client_logging_config(monkeypatch):
    # Set to DEBUG for a better idea of what is going on in this test.
    monkeypatch.setenv('LOG_LEVEL', 'ERROR')


def test_scheduler(geth_node, geth_node_config, deploy_client, deployed_contracts, contracts):
    block_sage = BlockSage(deploy_client)

    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.SpecifyBlock

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    anchor_block = deploy_client.get_block_number()

    blocks = (1, 4, 4, 8, 30, 40, 50, 60)

    call_keys = []

    for n in blocks:
        wait_for_transaction(deploy_client, client_contract.scheduleIt.sendTransaction(alarm._meta.address, anchor_block + 100 + n))

        last_call_key = alarm.getLastCallKey()
        assert last_call_key is not None

        call_keys.append(last_call_key)

    pool_manager = PoolManager(alarm, block_sage)
    scheduler = Scheduler(alarm, pool_manager, block_sage=block_sage)
    scheduler.monitor_async()

    final_block = anchor_block + 100 + 70
    wait_for_block(
        deploy_client,
        final_block,
        2 * block_sage.estimated_time_to_block(final_block),
    )

    scheduler.stop()
    block_sage.stop()

    results = [alarm.checkIfCalled(k) for k in call_keys]
    assert all(results)
