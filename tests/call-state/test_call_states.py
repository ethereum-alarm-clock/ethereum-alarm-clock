def test_call_cancellation_states_before_call_window(unmigrated_chain, web3,
                                                     deploy_fbc, CallStates):
    chain = unmigrated_chain
    client_contract = chain.get_contract('TestCallExecution')

    fbc = deploy_fbc(
        contract=client_contract,
        method_name='setBool',
        target_block=web3.eth.blockNumber + 300
    )

    assert fbc.call().state() == CallStates.Pending

    cancel_txn_hash = fbc.transact().cancel()
    chain.wait.for_receipt(cancel_txn_hash)

    assert fbc.call().state() == CallStates.Cancelled


def test_states_when_claimed(unmigrated_chain, web3, denoms, deploy_fbc,
                             CallStates):
    chain = unmigrated_chain
    client_contract = chain.get_contract('TestCallExecution')

    fbc = deploy_fbc(
        contract=client_contract,
        method_name='setBool',
        target_block=web3.eth.blockNumber + 300
    )

    assert fbc.call().state() == CallStates.Pending

    # wait until middle of claim window
    chain.wait.for_block(fbc.call().targetBlock() - 10 - 100)

    assert fbc.call().state() == CallStates.Unclaimed

    claim_txn_hash = fbc.transact({
        'value': 2 * denoms.ether,
    }).claim()
    chain.wait.for_receipt(claim_txn_hash)

    assert fbc.call().state() == CallStates.Claimed

    chain.wait.for_block(fbc.call().targetBlock() - 9)

    assert fbc.call().state() == CallStates.Frozen

    chain.wait.for_block(fbc.call().targetBlock())

    assert fbc.call().state() == CallStates.Callable

    execute_txn_hash = fbc.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert fbc.call().state() == CallStates.Executed


def test_states_when_unclaimed(unmigrated_chain, web3, denoms, deploy_fbc,
                               CallStates):
    chain = unmigrated_chain
    client_contract = chain.get_contract('TestCallExecution')

    fbc = deploy_fbc(
        contract=client_contract,
        method_name='setBool',
        target_block=web3.eth.blockNumber + 300
    )

    assert fbc.call().state() == CallStates.Pending

    chain.wait.for_block(fbc.call().targetBlock() - 9)

    assert fbc.call().state() == CallStates.Frozen

    chain.wait.for_block(fbc.call().targetBlock())

    assert fbc.call().state() == CallStates.Callable

    execute_txn_hash = fbc.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert fbc.call().state() == CallStates.Executed


def test_missed_state_when_claimed(unmigrated_chain, web3, denoms, deploy_fbc,
                                   CallStates):
    chain = unmigrated_chain
    client_contract = chain.get_contract('TestCallExecution')

    fbc = deploy_fbc(
        contract=client_contract,
        method_name='setBool',
        target_block=web3.eth.blockNumber + 300
    )

    assert fbc.call().state() == CallStates.Pending

    chain.wait.for_block(fbc.call().targetBlock() - 10 - 100)

    assert fbc.call().state() == CallStates.Unclaimed

    claim_txn_hash = fbc.transact({'value': 2 * denoms.ether}).claim()
    chain.wait.for_receipt(claim_txn_hash)

    assert fbc.call().state() == CallStates.Claimed

    chain.wait.for_block(fbc.call().targetBlock())

    assert fbc.call().state() == CallStates.Callable

    chain.wait.for_block(fbc.call().targetBlock() + fbc.call().gracePeriod())

    assert fbc.call().state() == CallStates.Missed


def test_missed_state_when_not_claimed(unmigrated_chain, web3, denoms,
                                       deploy_fbc, CallStates):
    chain = unmigrated_chain
    client_contract = chain.get_contract('TestCallExecution')

    fbc = deploy_fbc(
        contract=client_contract,
        method_name='setBool',
        target_block=web3.eth.blockNumber + 300
    )

    assert fbc.call().state() == CallStates.Pending

    chain.wait.for_block(fbc.call().targetBlock() - 10 - 100)

    assert fbc.call().state() == CallStates.Unclaimed

    chain.wait.for_block(fbc.call().targetBlock())

    assert fbc.call().state() == CallStates.Callable

    chain.wait.for_block(fbc.call().targetBlock() + fbc.call().gracePeriod())

    assert fbc.call().state() == CallStates.Missed
