from populus.contracts import (
    get_max_gas,
    deploy_contract,
    get_contract_address_from_txn,
)
from populus.utils import wait_for_transaction, wait_for_block


deploy_max_wait = 30
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_free_for_all_window_awards_mega_bonus(geth_node, geth_coinbase, rpc_client, deployed_contracts, contracts):
    alarm = deployed_contracts.Alarm
    caller_pool = contracts.CallerPool(alarm.getCallerPoolAddress.call(), rpc_client)
    client_contract = deployed_contracts.NoArgs
    joiner_a = deployed_contracts.JoinsPool
    deploy_txn = deploy_contract(rpc_client, contracts.JoinsPool, _from=geth_coinbase, gas=get_max_gas(rpc_client))
    joiner_b = contracts.JoinsPool(get_contract_address_from_txn(rpc_client, deploy_txn, 30), rpc_client)

    # Put in our deposit with the alarm contract.
    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    wait_for_transaction(rpc_client, joiner_a.setCallerPool.sendTransaction(caller_pool._meta.address))
    wait_for_transaction(rpc_client, joiner_b.setCallerPool.sendTransaction(caller_pool._meta.address))

    assert caller_pool.callerBonds.call(geth_coinbase) == 0
    deposit_amount = caller_pool.getMinimumBond.call() * 10
    # Put in our bond
    wait_for_transaction(
        rpc_client, caller_pool.depositBond.sendTransaction(value=deposit_amount)
    )

    # Put contract A's bond in
    wait_for_transaction(
        rpc_client,
        rpc_client.send_transaction(to=joiner_a._meta.address, value=deposit_amount)
    )
    wait_for_transaction(
        rpc_client, joiner_a.deposit.sendTransaction(deposit_amount)
    )
    # Put contract B's bond in
    wait_for_transaction(
        rpc_client,
        rpc_client.send_transaction(to=joiner_b._meta.address, value=deposit_amount)
    )
    wait_for_transaction(
        rpc_client, joiner_b.deposit.sendTransaction(deposit_amount)
    )

    # All join the pool
    wait_for_transaction(rpc_client, joiner_a.enter.sendTransaction())
    wait_for_transaction(rpc_client, joiner_b.enter.sendTransaction())
    wait_for_transaction(rpc_client, caller_pool.enterPool.sendTransaction())

    # New pool is formed but not active
    first_pool_key = caller_pool.getNextPoolKey.call()
    assert first_pool_key > 0

    # Wait for it to become active
    wait_for_block(rpc_client, first_pool_key, 180)

    # We should both be in the pool
    assert caller_pool.getActivePoolKey.call() == first_pool_key
    assert caller_pool.isInPool.call(joiner_a._meta.address, first_pool_key) is True
    assert caller_pool.isInPool.call(joiner_b._meta.address, first_pool_key) is True
    assert caller_pool.isInPool.call(geth_coinbase, first_pool_key) is True

    # Schedule the function call.
    txn_hash = client_contract.setGracePeriod.sendTransaction(24)
    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    target_block = alarm.getCallTargetBlock.call(callKey)
    grace_period = alarm.getCallGracePeriod.call(callKey)

    wait_for_block(rpc_client, target_block + grace_period - 4, 300)

    my_before_balance = caller_pool.callerBonds.call(geth_coinbase)
    before_balance_a = caller_pool.callerBonds.call(joiner_a._meta.address)
    before_balance_b = caller_pool.callerBonds.call(joiner_b._meta.address)
    assert alarm.checkIfCalled.call(callKey) is False

    call_txn_hash = alarm.doCall.sendTransaction(callKey)
    call_txn_receipt = wait_for_transaction(alarm._meta.rpc_client, call_txn_hash)
    call_txn = rpc_client.get_transaction_by_hash(call_txn_hash)
    call_block = rpc_client.get_block_by_hash(call_txn_receipt['blockHash'])

    my_after_balance = caller_pool.callerBonds.call(geth_coinbase)
    after_balance_a = caller_pool.callerBonds.call(joiner_a._meta.address)
    after_balance_b = caller_pool.callerBonds.call(joiner_b._meta.address)
    assert alarm.checkIfCalled.call(callKey) is True

    assert after_balance_a < before_balance_a
    assert after_balance_b < before_balance_b

    minimum_bond = int(call_block['gasLimit'], 16) * int(call_txn['gasPrice'], 16)
    assert after_balance_a == before_balance_a - minimum_bond
    assert after_balance_b == before_balance_b - minimum_bond

    assert my_after_balance > my_before_balance
    assert my_after_balance == my_before_balance + 2 * minimum_bond

    assert caller_pool.getNextPoolKey.call() == 0
