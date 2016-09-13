def test_anyone_can_cancel_after_call_window(chain, web3, deploy_fbc):
    client_contract = chain.get_contract('TestCallExecution')

    target_block = web3.eth.blockNumber + 300

    fbc = deploy_fbc(
        contract=client_contract,
        method_name='setBool',
        target_block=target_block,
    )

    chain.wait.for_block(target_block + fbc.call().gracePeriod() + 1)

    assert fbc.call().isCancelled() is False

    cancel_txn_h = fbc.transact({'from': web3.eth.accounts[1]}).cancel()
    chain.wait.for_receipt(cancel_txn_h)

    cancel_txn = web3.eth.getTransaction(cancel_txn_h)

    scheduler_address = fbc.call().schedulerAddress()

    # sanity
    assert cancel_txn['from'] != scheduler_address
    assert cancel_txn['from'] == web3.eth.accounts[1]

    assert fbc.call().isCancelled() is True
