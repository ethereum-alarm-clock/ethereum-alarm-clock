def test_cannot_cancel_if_already_cancelled(chain, web3, deploy_fbc, CallLib):
    client_contract = chain.get_contract('TestCallExecution')

    target_block = web3.eth.blockNumber + 300
    fbc = deploy_fbc(
        contract=client_contract,
        method_name='setBool',
        target_block=target_block,
    )

    assert fbc.call().isCancelled() is False

    cancel_txn_h = fbc.transact().cancel()
    chain.wait.for_receipt(cancel_txn_h)

    assert fbc.call().isCancelled() is True

    duplicate_cancel_txn_h = fbc.transact().cancel()
    chain.wait.for_receipt(duplicate_cancel_txn_h)

    cancel_filter = CallLib.pastEvents('Cancelled', {'address': fbc.address})
    cancel_logs = cancel_filter.get()
    assert len(cancel_logs) == 1
    cancel_log_data = cancel_logs[0]
    assert cancel_log_data['transactionHash'] == cancel_txn_h
