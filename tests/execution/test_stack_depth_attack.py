def test_stack_depth_does_not_call_if_cannot_reach_depth(chain, web3, deploy_fbc, CallLib):
    client_contract = chain.get_contract('TestErrors')

    fbc = deploy_fbc(
        client_contract,
        method_name='doStackExtension',
        arguments=[340],
        require_depth=1000,
    )
    assert fbc.call().requiredStackDepth() == 1000

    set_txn_hash = client_contract.transact().setCallAddress(fbc.address)
    chain.wait.for_receipt(set_txn_hash)

    chain.wait.for_block(fbc.call().targetBlock())

    assert client_contract.call().value() is False

    # Call such that the stack has been "significantly" extended prior to
    # executing the call.
    bad_call_txn_hash = client_contract.transact().proxyCall(1000)
    chain.wait.for_receipt(bad_call_txn_hash)

    assert fbc.call().wasCalled() is False
    assert client_contract.call().value() is False

    abort_filter = CallLib.pastEvents('CallAborted', {'address': fbc.address})
    abort_logs = abort_filter.get()
    assert len(abort_logs) == 1
    abort_log_data = abort_logs[0]
    reason = abort_log_data['args']['reason'].replace('\x00', '')
    assert reason == 'STACK_TOO_DEEP'

    execute_txn_hash = client_contract.transact().proxyCall(0)
    chain.wait.for_receipt(execute_txn_hash)

    assert fbc.call().wasCalled() is True
    assert client_contract.call().value() is True
