def test_only_scheduler_can_cancel_prior_to_target_block(chain,
                                                         web3,
                                                         deploy_fbc,
                                                         CallLib):
    target_block = web3.eth.blockNumber + 300

    fbc = deploy_fbc(target_block=target_block)

    assert fbc.call().isCancelled() is False

    cancel_txn_hash = fbc.transact({'from': web3.eth.accounts[1]}).cancel()
    chain.wait.for_receipt(cancel_txn_hash)

    assert fbc.call().isCancelled() is False

    cancel_filter = CallLib.pastEvents('Cancelled', {'address': fbc.address})
    cancel_logs = cancel_filter.get()
    assert len(cancel_logs) == 0
