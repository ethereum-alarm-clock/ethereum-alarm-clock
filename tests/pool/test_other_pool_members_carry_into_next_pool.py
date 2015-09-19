from populus.utils import wait_for_transaction, wait_for_block


deploy_max_wait = 30
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_pool_membership_is_carried_over(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    caller_pool = deployed_contracts.CallerPool
    joiner = deployed_contracts.JoinsPool

    wait_for_transaction(rpc_client, joiner.setCallerPool.sendTransaction(caller_pool._meta.address))

    assert caller_pool.callerBonds.call(geth_coinbase) == 0
    deposit_amount = caller_pool.getMinimumBond.call() * 10

    wait_for_transaction(
        rpc_client, caller_pool.depositBond.sendTransaction(value=deposit_amount)
    )
    wait_for_transaction(
        rpc_client,
        rpc_client.send_transaction(to=joiner._meta.address, value=deposit_amount)
    )

    wait_for_transaction(
        rpc_client, joiner.deposit.sendTransaction(deposit_amount)
    )

    wait_for_transaction(rpc_client, joiner.enter.sendTransaction())

    first_pool_key = caller_pool.getNextPoolKey.call()
    assert first_pool_key > 0

    wait_for_transaction(rpc_client, caller_pool.enterPool.sendTransaction())
    wait_for_block(rpc_client, first_pool_key, 180)

    assert caller_pool.getActivePoolKey.call() == first_pool_key
    assert caller_pool.isInPool.call(first_pool_key) is True

    wait_for_transaction(rpc_client, joiner.exit.sendTransaction())
    second_pool_key = caller_pool.getNextPoolKey.call()

    assert second_pool_key > first_pool_key

    wait_for_block(rpc_client, second_pool_key, 180)

    assert caller_pool.getActivePoolKey.call() == second_pool_key
    assert caller_pool.isInPool.call(second_pool_key) is True
