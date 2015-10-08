from populus.utils import wait_for_transaction, wait_for_block


deploy_contracts = [
    "CallerPool",
    "JoinsPool",
]


def test_pool_membership_frozen_during_transition_period(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    caller_pool = deployed_contracts.CallerPool
    joiner = deployed_contracts.JoinsPool

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
    wait_for_transaction(rpc_client, joiner.enter.sendTransaction())

    # New pool is formed but not active
    first_pool_key = caller_pool.getNextPoolKey.call()
    assert first_pool_key > 0

    # Only the contract is in the pool. (but it isn't active yet)
    assert caller_pool.getActivePoolKey.call() == 0
    assert caller_pool.isInPool.call(joiner._meta.address, first_pool_key) is True
    assert caller_pool.isInPool.call(geth_coinbase, first_pool_key) is False

    # Now we join the pool
    wait_for_transaction(rpc_client, caller_pool.enterPool.sendTransaction())

    # Both are in the pool but it isn't active yet
    assert caller_pool.getActivePoolKey.call() == 0
    assert caller_pool.getNextPoolKey.call() == first_pool_key
    assert caller_pool.isInPool.call(joiner._meta.address, first_pool_key) is True
    assert caller_pool.isInPool.call(geth_coinbase, first_pool_key) is True

    # Wait for it to become active
    wait_for_block(rpc_client, first_pool_key, 180)
    assert caller_pool.getActivePoolKey.call() == first_pool_key
    assert caller_pool.getNextPoolKey.call() == 0

    # Now the contract leaves the pool.
    wait_for_transaction(rpc_client, joiner.exit.sendTransaction())
    second_pool_key = caller_pool.getNextPoolKey.call()

    # New pool should have been setup
    assert second_pool_key > first_pool_key

    # joiner should not be in next pool.
    assert caller_pool.isInPool.call(joiner._meta.address, second_pool_key) is False

    # should still be in the pool until it becomes active
    assert caller_pool.isInPool.call(joiner._meta.address, first_pool_key) is True
    assert caller_pool.isInPool.call(geth_coinbase, first_pool_key) is True

    # should still be allowed to leave
    assert caller_pool.canExitPool.call(geth_coinbase) is True

    # wait for the pool to become active
    wait_for_block(rpc_client, second_pool_key - 20, 180)

    # should no longer be allowed to leave (within freeze window)
    assert caller_pool.canExitPool.call(geth_coinbase) is False

    # wait for the pool to become active
    wait_for_block(rpc_client, second_pool_key, 180)

    # should now be allowed to leave.
    assert caller_pool.canExitPool.call(geth_coinbase) is True
