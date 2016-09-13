def test_cancelling_a_call_before_bid_window(chain, web3, deploy_fbc, CallLib):
    client_contract = chain.get_contract('TestCallExecution')

    target_block = web3.eth.blockNumber + 300
    fbc = deploy_fbc(
        contract=client_contract,
        method_name='setBool',
        target_block=target_block,
    )

    first_bid_block = target_block - 240 - 15 - 10

    chain.wait.for_block(first_bid_block - 1)

    assert fbc.call().isCancelled() is False

    cancel_txn_h = fbc.transact().cancel()
    cancel_txn_r = chain.wait.for_receipt(cancel_txn_h)

    assert cancel_txn_r['blockNumber'] == first_bid_block - 1

    assert fbc.call().isCancelled() is True

    cancel_filter = CallLib.pastEvents('Cancelled', {'address': fbc.address})
    cancel_logs = cancel_filter.get()
    assert len(cancel_logs) == 1

    cancel_log_data = cancel_logs[0]
    assert cancel_log_data['args']['cancelled_by'] == web3.eth.coinbase


def test_cancelling_a_call_after_call_window(chain, web3, deploy_fbc, CallLib):
    client_contract = chain.get_contract('TestCallExecution')

    target_block = web3.eth.blockNumber + 20
    fbc = deploy_fbc(
        contract=client_contract,
        method_name='setBool',
        target_block=target_block,
    )

    chain.wait.for_block(target_block + 256)

    assert fbc.call().isCancelled() is False

    cancel_txn_hash = fbc.transact().cancel()
    chain.wait.for_receipt(cancel_txn_hash)

    cancel_filter = CallLib.pastEvents('Cancelled', {'address': fbc.address})
    cancel_logs = cancel_filter.get()
    assert len(cancel_logs) == 1

    cancel_log_data = cancel_logs[0]
    assert cancel_log_data['args']['cancelled_by'] == web3.eth.coinbase

    assert fbc.call().isCancelled() is True
