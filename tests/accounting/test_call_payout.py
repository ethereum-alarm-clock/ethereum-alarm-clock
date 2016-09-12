def test_execution_payment(chain, web3, FutureBlockCall, CallLib,
                           deploy_fbc):
    client_contract = chain.get_contract('TestCallExecution')

    target_block = web3.eth.blockNumber + 20

    fbc = deploy_fbc(
        contract=client_contract,
        method_name='setBool',
        target_block=target_block,
        payment=12345,
        donation=54321,
    )

    chain.wait.for_block(target_block)

    assert web3.eth.getBalance(client_contract.address) == 0

    assert client_contract.call().v_bool() is False
    assert client_contract.call().wasSuccessful() == 0

    assert fbc.call().wasCalled() is False

    call_txn_hash = client_contract.transact().doExecution(fbc.address)
    chain.wait.for_receipt(call_txn_hash)

    assert fbc.call().wasCalled() is True
    assert fbc.call().wasSuccessful() is True

    assert client_contract.call().wasSuccessful() == 1
    assert client_contract.call().v_bool() is True

    filter = CallLib().pastEvents('CallExecuted', {'address': fbc.address})
    events = filter.get()

    assert len(events) == 1
    event = events[0]

    assert 'gasCost' in event['args']
    expected_payout = 12345 + event['args']['gasCost']

    assert event['args']['payment'] == expected_payout
    assert web3.eth.getBalance(client_contract.address) == event['args']['payment']
