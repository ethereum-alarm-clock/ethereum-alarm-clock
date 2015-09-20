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
    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    target_block = alarm.getCallTargetBlock.call(callKey)
    grace_period = alarm.getCallGracePeriod.call(callKey)

    callers = [
        caller_pool.getCallerFromPool.call(callKey, target_block, grace_period, target_block + n)
        for n in range(grace_period)
    ]
    caller_a = callers[0]
    caller_b = callers[4]

    assert {geth_coinbase, joiner._meta.address, '0x0000000000000000000000000000000000000000'} == set(callers)

    call_on_block = None

    for i, caller in enumerate(callers):
        if i / 4 + 1 > len(callers) / 4:
            assert caller == '0x0000000000000000000000000000000000000000'
        elif (i / 4) % 2 == 0:
            assert caller == caller_a
        else:
            assert caller == caller_b

        if call_on_block is None and i > 4 and caller == geth_coinbase:
            call_on_block = target_block + i * 4

    wait_for_block(rpc_client, call_on_block, 240)

    assert caller_pool.getNextPoolKey.call() == 0
    before_balance = caller_pool.callerBonds.call(joiner._meta.address)
    assert alarm.checkIfCalled.call(callKey) is False

    call_txn_hash = alarm.doCall.sendTransaction(callKey)
    call_txn_receipt = wait_for_transaction(alarm._meta.rpc_client, call_txn_hash)
    call_txn = rpc_client.get_transaction_by_hash(call_txn_hash)
    call_block = rpc_client.get_block_by_hash(call_txn_receipt['blockHash'])

    after_balance = caller_pool.callerBonds.call(joiner._meta.address)
    assert alarm.checkIfCalled.call(callKey) is True

    assert after_balance < before_balance

    minimum_bond = int(call_block['gasLimit'], 16) * int(call_txn['gasPrice'], 16)
    assert after_balance == before_balance - minimum_bond

    next_pool_key = caller_pool.getNextPoolKey.call()
    assert next_pool_key > 0

    assert caller_pool.isInPool.call(joiner._meta.address, first_pool_key) is True
    assert caller_pool.isInPool.call(joiner._meta.address, next_pool_key) is False
