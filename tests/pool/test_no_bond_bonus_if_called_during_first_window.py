deploy_contracts = [
    "Scheduler",
    "JoinsPool",
    "TestCallExecution",
]


def test_no_bond_bonus_for_first_call_window(deploy_client, deployed_contracts,
                                             contracts, deploy_coinbase,
                                             get_call, get_execution_data,
                                             denoms):
    scheduler = deployed_contracts.Scheduler
    joiner = deployed_contracts.JoinsPool
    client_contract = deployed_contracts.TestCallExecution

    deploy_client.wait_for_transaction(
        joiner.setCallerPool(scheduler._meta.address),
    )

    assert scheduler.getBondBalance(deploy_coinbase) == 0
    deposit_amount = scheduler.getMinimumBond() * 10
    # Put in our bond
    deploy_client.wait_for_transaction(
        scheduler.depositBond(value=deposit_amount)
    )

    # Put the contract's bond in
    deploy_client.wait_for_transaction(
        deploy_client.send_transaction(to=joiner._meta.address, value=deposit_amount)
    )
    deploy_client.wait_for_transaction(
        joiner.deposit(deposit_amount)
    )

    # Both join the pool
    deploy_client.wait_for_transaction(joiner.enter())
    deploy_client.wait_for_transaction(scheduler.enterPool())

    # New pool is formed but not active
    first_generation_id = scheduler.getNextGenerationId()
    assert first_generation_id > 0

    # Wait for it to become active
    deploy_client.wait_for_block(scheduler.getGenerationStartAt(first_generation_id), 180)

    # We should both be in the pool
    assert scheduler.getCurrentGenerationId() == first_generation_id
    assert scheduler.isInGeneration(joiner._meta.address, first_generation_id) is True
    assert scheduler.isInGeneration(deploy_coinbase, first_generation_id) is True

    # Schedule the function call.
    for _ in range(5):
        # Schedule the function call.
        scheduling_txn = scheduler.scheduleCall(
            client_contract._meta.address,
            client_contract.setBool.encoded_abi_signature,
            deploy_client.get_block_number() + 250,
            1000000,
            value=10 * denoms.ether,
            gas=3000000,
        )
        scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn)
        call = get_call(scheduling_txn)

        target_block = call.targetBlock()
        grace_period = call.gracePeriod()
        first_caller = scheduler.getDesignatedCaller(call._meta.address, target_block)[1]
        if first_caller == deploy_coinbase[2:]:
            break
    else:
        raise ValueError("Was never first caller")

    deploy_client.wait_for_block(target_block, 240)

    before_balance = scheduler.getBondBalance(joiner._meta.address)

    call_txn_hash = scheduler.execute(call._meta.address)
    deploy_client.wait_for_transaction(call_txn_hash)

    after_balance = scheduler.getBondBalance(joiner._meta.address)

    execution_data = get_execution_data(call_txn_hash)

    assert after_balance == before_balance
