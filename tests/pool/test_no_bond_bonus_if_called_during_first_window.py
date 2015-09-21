from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction, wait_for_block


deploy_max_wait = 30
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_call_window_divided_between_callers(geth_node, geth_coinbase, rpc_client, deployed_contracts, contracts):
    alarm = deployed_contracts.Alarm
    caller_pool = contracts.CallerPool(alarm.getCallerPoolAddress.call(), rpc_client)
    joiner = deployed_contracts.JoinsPool
    client_contract = deployed_contracts.NoArgs

    # Put in our deposit with the alarm contract.
    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    wait_for_transaction(rpc_client, joiner.setCallerPool.sendTransaction(caller_pool._meta.address))

    assert caller_pool.callerBonds.call(geth_coinbase) == 0
    deposit_amount = caller_pool.getMinimumBond.call() * 10
    # Put in our bond
    wait_for_transaction(
        rpc_client, caller_pool.depositBond.sendTransaction(value=deposit_amount)
    )

    # Put the contract's bond in
    wait_for_transaction(
        rpc_client,
        rpc_client.send_transaction(to=joiner._meta.address, value=deposit_amount)
    )
    wait_for_transaction(
        rpc_client, joiner.deposit.sendTransaction(deposit_amount)
    )

    # Both join the pool
    wait_for_transaction(rpc_client, joiner.enter.sendTransaction())
    wait_for_transaction(rpc_client, caller_pool.enterPool.sendTransaction())

    # New pool is formed but not active
    first_pool_key = caller_pool.getNextPoolKey.call()
    assert first_pool_key > 0

    # Wait for it to become active
    wait_for_block(rpc_client, first_pool_key, 180)

    # We should both be in the pool
    assert caller_pool.getActivePoolKey.call() == first_pool_key
    assert caller_pool.isInPool.call(joiner._meta.address, first_pool_key) is True
    assert caller_pool.isInPool.call(geth_coinbase, first_pool_key) is True

    # Schedule the function call.
    for _ in range(5):
        txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
        wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

        callKey = alarm.getLastCallKey.call()
        assert callKey is not None

        target_block = alarm.getCallTargetBlock.call(callKey)
        grace_period = alarm.getCallGracePeriod.call(callKey)
        first_caller = caller_pool.getDesignatedCaller.call(callKey, target_block, grace_period, target_block)
        if first_caller == geth_coinbase:
            break
    else:
        raise ValueError("Was never first caller")

    wait_for_block(rpc_client, target_block, 240)

    before_balance = caller_pool.callerBonds.call(joiner._meta.address)
    assert alarm.checkIfCalled.call(callKey) is False

    call_txn_hash = alarm.doCall.sendTransaction(callKey)
    wait_for_transaction(alarm._meta.rpc_client, call_txn_hash)

    after_balance = caller_pool.callerBonds.call(joiner._meta.address)
    assert alarm.checkIfCalled.call(callKey) is True

    assert after_balance == before_balance
