deploy_contracts = [
    "Scheduler",
    "JoinsPool",
    "TestCallExecution",
]


def test_call_window_divided_between_callers(deploy_client, deployed_contracts,
                                             contracts, deploy_coinbase, get_call,
                                             get_execution_data, denoms):
    scheduler = deployed_contracts.Scheduler
    joiner = deployed_contracts.JoinsPool
    client_contract = deployed_contracts.TestCallExecution

    deploy_client.wait_for_transaction(joiner.setCallerPool(scheduler._meta.address))

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
    assert scheduler.canEnterPool(joiner._meta.address) is True
    deploy_client.wait_for_transaction(joiner.enter())
    assert scheduler.canEnterPool(deploy_coinbase) is True
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

    assert scheduler.getGenerationIdForCall(call._meta.address) == first_generation_id

    target_block = call.targetBlock()
    grace_period = call.gracePeriod()
    call_window_size = scheduler.getCallWindowSize()

    callers = [
        scheduler.getDesignatedCaller(call._meta.address, target_block + n)[1]
        for n in range(grace_period)
    ]
    caller_set_a = set(callers[:call_window_size])
    caller_set_b = set(callers[call_window_size:2 * call_window_size])

    # sanity check
    assert len(caller_set_a) == 1
    assert len(caller_set_b) == 1

    caller_a = tuple(caller_set_a)[0]
    caller_b = tuple(caller_set_b)[0]

    assert caller_a != caller_b

    assert {deploy_coinbase, joiner._meta.address, '0x0000000000000000000000000000000000000000'} == set(callers)

    call_on_block = None
    call_window_size = scheduler.getCallWindowSize()

    for i, caller in enumerate(callers):
        if i / call_window_size + 2 > len(callers) / call_window_size:
            assert caller == '0x0000000000000000000000000000000000000000'
        elif (i / call_window_size) % 2 == 0:
            assert caller == caller_a
        else:
            assert caller == caller_b

        if call_on_block is None and i > call_window_size and caller == deploy_coinbase:
            call_on_block = target_block + i

    assert call_on_block is not None

    deploy_client.wait_for_block(call_on_block, 240)

    assert scheduler.getNextGenerationId() == 0
    before_balance = scheduler.getBondBalance(joiner._meta.address)

    call_txn_hash = scheduler.execute(call._meta.address)
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)
    call_txn = deploy_client.get_transaction_by_hash(call_txn_hash)
    call_block = deploy_client.get_block_by_hash(call_txn_receipt['blockHash'])

    after_balance = scheduler.getBondBalance(joiner._meta.address)

    execution_data = get_execution_data(call_txn_hash)
    assert execution_data['success'] is True

    assert after_balance < before_balance

    minimum_bond = int(call_block['gasLimit'], 16) * int(call_txn['gasPrice'], 16)
    assert after_balance == before_balance - minimum_bond

    next_generation_id = scheduler.getNextGenerationId()
    assert next_generation_id > 0

    assert scheduler.isInGeneration(joiner._meta.address, first_generation_id) is True
    assert scheduler.isInGeneration(joiner._meta.address, next_generation_id) is False
