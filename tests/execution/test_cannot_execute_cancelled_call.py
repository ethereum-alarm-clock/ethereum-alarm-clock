def test_cannot_execute_cancelled_call(chain, web3, deploy_fbc, CallLib):
    client_contract = chain.get_contract('TestCallExecution')

    target_block = web3.eth.blockNumber + 20
    fbc = deploy_fbc(client_contract, target_block=target_block)

    # cancel it
    cancel_txn_h = fbc.transact().cancel()
    chain.wait.for_receipt(cancel_txn_h)

    assert fbc.call().isCancelled() is True

    chain.wait.for_block(target_block)

    assert fbc.call().wasCalled() is False

    txn_h = fbc.transact().execute()
    chain.wait.for_receipt(txn_h)

    assert fbc.call().wasCalled() is False
