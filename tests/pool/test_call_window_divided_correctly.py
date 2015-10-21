from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "JoinsPool",
    "NoArgs",
]


def test_call_window_divided_between_callers(deploy_client, deployed_contracts, contracts):
    alarm = deployed_contracts.Alarm
    joiner = deployed_contracts.JoinsPool
    client_contract = deployed_contracts.NoArgs
    coinbase = deploy_client.get_coinbase()

    # Put in our deposit with the alarm contract.
    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    wait_for_transaction(deploy_client, joiner.setCallerPool.sendTransaction(alarm._meta.address))

    assert alarm.getBondBalance(coinbase) == 0
    deposit_amount = alarm.getMinimumBond() * 10
    # Put in our bond
    wait_for_transaction(
        deploy_client, alarm.depositBond.sendTransaction(value=deposit_amount)
    )

    # Put the contract's bond in
    wait_for_transaction(
        deploy_client,
        deploy_client.send_transaction(to=joiner._meta.address, value=deposit_amount)
    )
    wait_for_transaction(
        deploy_client, joiner.deposit.sendTransaction(deposit_amount)
    )

    # Both join the pool
    assert alarm.canEnterPool(joiner._meta.address) is True
    wait_for_transaction(deploy_client, joiner.enter.sendTransaction())
    assert alarm.canEnterPool(coinbase) is True
    wait_for_transaction(deploy_client, alarm.enterPool.sendTransaction())

    # New pool is formed but not active
    first_generation_id = alarm.getNextGenerationId()
    assert first_generation_id > 0

    # Wait for it to become active
    deploy_client.wait_for_block(alarm.getGenerationStartAt(first_generation_id), 180)

    # We should both be in the pool
    assert alarm.getCurrentGenerationId() == first_generation_id
    assert alarm.isInGeneration(joiner._meta.address, first_generation_id) is True
    assert alarm.isInGeneration(coinbase, first_generation_id) is True

    # Schedule the function call.
    wait_for_transaction(deploy_client, client_contract.setDelta(250))
    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(deploy_client, txn_hash)

    call_key = alarm.getLastCallKey()
    assert call_key is not None

    assert alarm.getGenerationIdForCall(call_key) == first_generation_id

    target_block = alarm.getCallTargetBlock(call_key)
    grace_period = alarm.getCallGracePeriod(call_key)
    call_window_size = alarm.getCallWindowSize()

    callers = [
        alarm.getDesignatedCaller(call_key, target_block + n)
        for n in range(grace_period)
    ]
    caller_a = callers[0]
    caller_b = callers[call_window_size]

    # sanity check
    assert caller_a != caller_b

    assert {coinbase, joiner._meta.address, '0x0000000000000000000000000000000000000000'} == set(callers)

    call_on_block = None
    call_window_size = alarm.getCallWindowSize()

    for i, caller in enumerate(callers):
        if i / call_window_size + 2 > len(callers) / call_window_size:
            assert caller == '0x0000000000000000000000000000000000000000'
        elif (i / call_window_size) % 2 == 0:
            assert caller == caller_a
        else:
            assert caller == caller_b

        if call_on_block is None and i > call_window_size and caller == coinbase:
            call_on_block = target_block + i

    deploy_client.wait_for_block(call_on_block, 240)

    assert alarm.getNextGenerationId() == 0
    before_balance = alarm.getBondBalance(joiner._meta.address)
    assert alarm.checkIfCalled(call_key) is False

    call_txn_hash = alarm.doCall.sendTransaction(call_key)
    call_txn_receipt = wait_for_transaction(deploy_client, call_txn_hash)
    call_txn = deploy_client.get_transaction_by_hash(call_txn_hash)
    call_block = deploy_client.get_block_by_hash(call_txn_receipt['blockHash'])

    after_balance = alarm.getBondBalance(joiner._meta.address)
    assert alarm.checkIfCalled(call_key) is True

    assert after_balance < before_balance

    minimum_bond = int(call_block['gasLimit'], 16) * int(call_txn['gasPrice'], 16)
    assert after_balance == before_balance - minimum_bond

    next_generation_id = alarm.getNextGenerationId()
    assert next_generation_id > 0

    assert alarm.isInGeneration(joiner._meta.address, first_generation_id) is True
    assert alarm.isInGeneration(joiner._meta.address, next_generation_id) is False
