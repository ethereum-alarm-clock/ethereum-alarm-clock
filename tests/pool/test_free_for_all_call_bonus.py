from populus.contracts import (
    deploy_contract,
)
from populus.utils import (
    get_contract_address_from_txn,
)


deploy_contracts = [
    "Scheduler",
    "JoinsPool",
    "TestCallExecution",
]


def test_free_for_all_window_awards_mega_bonus(deploy_client,
                                               deployed_contracts, contracts,
                                               deploy_coinbase,
                                               get_call,
                                               get_execution_data,
                                               denoms):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution
    joiner_a = deployed_contracts.JoinsPool

    deploy_txn = deploy_contract(
        deploy_client,
        contracts.JoinsPool,
        _from=deploy_coinbase,
        gas=deploy_client.get_max_gas(),
    )
    joiner_b = contracts.JoinsPool(get_contract_address_from_txn(deploy_client, deploy_txn, 30), deploy_client)

    # Put in our deposit with the scheduler contract.
    deposit_amount = deploy_client.get_max_gas() * deploy_client.get_gas_price() * 20

    deploy_client.wait_for_transaction(
        joiner_a.setCallerPool.sendTransaction(scheduler._meta.address),
    )
    deploy_client.wait_for_transaction(
        joiner_b.setCallerPool.sendTransaction(scheduler._meta.address),
    )

    assert scheduler.getBondBalance(deploy_coinbase) == 0
    deposit_amount = scheduler.getMinimumBond() * 10
    # Put in our bond
    deploy_client.wait_for_transaction(
        scheduler.depositBond.sendTransaction(value=deposit_amount)
    )

    # Put contract A's bond in
    deploy_client.wait_for_transaction(
        deploy_client.send_transaction(to=joiner_a._meta.address, value=deposit_amount)
    )
    deploy_client.wait_for_transaction(
        joiner_a.deposit.sendTransaction(deposit_amount)
    )
    # Put contract B's bond in
    deploy_client.wait_for_transaction(
        deploy_client.send_transaction(to=joiner_b._meta.address, value=deposit_amount)
    )
    deploy_client.wait_for_transaction(
        joiner_b.deposit.sendTransaction(deposit_amount)
    )

    # All join the pool
    deploy_client.wait_for_transaction(joiner_a.enter.sendTransaction())
    deploy_client.wait_for_transaction(joiner_b.enter.sendTransaction())
    deploy_client.wait_for_transaction(scheduler.enterPool.sendTransaction())

    # New pool is formed but not active
    first_generation_id = scheduler.getNextGenerationId()
    assert first_generation_id > 0

    # Wait for it to become active
    deploy_client.wait_for_block(scheduler.getGenerationStartAt(first_generation_id), 240)

    # We should both be in the pool
    assert scheduler.getCurrentGenerationId() == first_generation_id
    assert scheduler.isInGeneration(joiner_a._meta.address, first_generation_id) is True
    assert scheduler.isInGeneration(joiner_b._meta.address, first_generation_id) is True
    assert scheduler.isInGeneration(deploy_coinbase, first_generation_id) is True

    # Schedule the function call.
    scheduling_txn = scheduler.scheduleCall(
        client_contract._meta.address,
        client_contract.setBool.encoded_abi_signature,
        deploy_client.get_block_number() + 45,
        1000000,
        scheduler.getMinimumGracePeriod(),
        value=10 * denoms.ether,
        gas=3000000,
    )
    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn)
    call = get_call(scheduling_txn)

    target_block = call.targetBlock()
    grace_period = call.gracePeriod()

    deploy_client.wait_for_block(target_block + grace_period - 4, 300)

    my_before_balance = scheduler.getBondBalance(deploy_coinbase)
    before_balance_a = scheduler.getBondBalance(joiner_a._meta.address)
    before_balance_b = scheduler.getBondBalance(joiner_b._meta.address)

    call_txn_hash = scheduler.execute(call._meta.address)
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)
    call_txn = deploy_client.get_transaction_by_hash(call_txn_hash)
    call_block = deploy_client.get_block_by_hash(call_txn_receipt['blockHash'])

    execution_data = get_execution_data(call_txn_hash)
    assert execution_data['success'] is True

    my_after_balance = scheduler.getBondBalance(deploy_coinbase)
    after_balance_a = scheduler.getBondBalance(joiner_a._meta.address)
    after_balance_b = scheduler.getBondBalance(joiner_b._meta.address)

    assert after_balance_a < before_balance_a
    assert after_balance_b < before_balance_b

    minimum_bond = int(call_block['gasLimit'], 16) * int(call_txn['gasPrice'], 16)
    assert after_balance_a == before_balance_a - minimum_bond
    assert after_balance_b == before_balance_b - minimum_bond

    assert my_after_balance > my_before_balance
    assert my_after_balance == my_before_balance + 2 * minimum_bond

    assert scheduler.getNextGenerationId() == 0
