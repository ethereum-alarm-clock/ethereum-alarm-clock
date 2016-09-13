def test_cannot_execute_after_call_window(chain, deploy_fbc, CallLib):
    client_contract = chain.get_contract('TestCallExecution')

    fbc = deploy_fbc(client_contract, method_name='setBool')

    chain.wait.for_block(fbc.call().targetBlock() + fbc.call().gracePeriod() + 1)

    assert fbc.call().wasCalled() is False

    txn_h = fbc.transact({'gas': 2000000}).execute()
    chain.wait.for_receipt(txn_h)

    assert fbc.call().wasCalled() is False
