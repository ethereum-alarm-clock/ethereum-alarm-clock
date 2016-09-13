def test_cancelling_a_call_during_bid_window(chain, web3, deploy_fbc, CallLib):
    client_contract = chain.get_contract('TestCallExecution')

    target_block = web3.eth.blockNumber + 300
    fbc = deploy_fbc(
        contract=client_contract,
        method_name='setBool',
        target_block=target_block,
    )

    first_bid_block = target_block - 240 - 15 - 10
    chain.wait.for_block(first_bid_block)

    assert fbc.call().isCancelled() is False

    cancel_txn = fbc.transact().cancel()
    chain.wait.for_receipt(cancel_txn)

    cancel_filter = CallLib.pastEvents('Cancelled', {'address': fbc.address})
    cancel_logs = cancel_filter.get()
    assert not cancel_logs

    assert fbc.call().isCancelled() is False
