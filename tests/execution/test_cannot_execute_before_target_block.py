def test_cannot_execute_before_target_block(chain, web3, deploy_fbc, CallLib):
    client_contract = chain.get_contract('TestCallExecution')

    target_block = web3.eth.blockNumber + 20
    fbc = deploy_fbc(client_contract, target_block=target_block)

    chain.wait.for_block(target_block - 4)

    assert fbc.call().wasCalled() is False

    txn_h = fbc.transact().execute()
    chain.wait.for_receipt(txn_h)

    assert fbc.call().wasCalled() is False
