from populus.contracts import get_max_gas
from populus.utils import (
    wait_for_transaction,
    wait_for_block,
)

from alarm_client.client import (
    Scheduler,
    PoolManager,
    BlockSage,
)


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_scheduler(geth_node, rpc_client, deployed_contracts, contracts):
    alarm = deployed_contracts.Alarm
    caller_pool = contracts.CallerPool(alarm.getCallerPoolAddress.call(), rpc_client)
    client_contract = deployed_contracts.SpecifyBlock

    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    anchor_block = rpc_client.get_block_number()

    blocks = (1, 4, 4, 8, 30, 40, 50, 60)

    call_keys = []

    block_sage = BlockSage(rpc_client)

    for n in blocks:
        wait_for_transaction(rpc_client, client_contract.scheduleIt.sendTransaction(alarm._meta.address, anchor_block + 100 + n))

        last_call_key = alarm.getLastCallKey.call()
        assert last_call_key is not None

        call_keys.append(last_call_key)

    pool_manager = PoolManager(caller_pool, block_sage)
    scheduler = Scheduler(alarm, pool_manager, block_sage)
    scheduler.monitor_async()

    final_block = anchor_block + 100 + 70
    wait_for_block(rpc_client, final_block, 600)

    scheduler.stop()
    block_sage.stop()

    results = [alarm.checkIfCalled.call(k) for k in call_keys]
    assert all(results)
