def test_cannot_cancel_if_already_called(chain, web3, deploy_fbc, CallLib):
    client_contract = chain.get_contract('TestCallExecution')

    target_block = web3.eth.blockNumber + 300
    fbc = deploy_fbc(
        contract=client_contract,
        method_name='setBool',
        target_block=target_block,
    )

    chain.wait.for_block(target_block)

    assert fbc.call().isCancelled() is False
    assert fbc.call().wasCalled() is False

    execute_txn_h = fbc.transact().execute()
    chain.wait.for_receipt(execute_txn_h)

    assert fbc.call().wasCalled() is True
    assert fbc.call().isCancelled() is False

    cancel_txn = fbc.transact().cancel()
    chain.wait.for_receipt(cancel_txn)

    assert fbc.call().wasCalled() is True
    assert fbc.call().isCancelled() is False

    cancel_filter = CallLib.pastEvents('Cancelled', {'address': fbc.address})
    cancel_logs = cancel_filter.get()
    assert not cancel_logs
