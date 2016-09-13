def test_canary_cancellation(chain, web3, deploy_canary, FutureBlockCall, denoms):
    scheduler = chain.get_contract('Scheduler')
    canary = deploy_canary()

    init_txn_h = canary.transact().initialize()
    chain.wait.for_receipt(init_txn_h)

    fbc_address = canary.call().callContractAddress()

    # check that the call was scheduled
    assert fbc_address != "0x0000000000000000000000000000000000000000"
    assert scheduler.call().isKnownCall(fbc_address) is True

    # check that the heartbeat went up
    assert canary.call().heartbeatCount() == 0

    fbc = FutureBlockCall(address=fbc_address)

    # check that it has enough funds to successfully heartbeat
    assert web3.eth.getBalance(canary.address) >= 2 * denoms.ether
    assert fbc.call().isCancelled() is False

    cancel_txn_h = canary.transact().cancel()
    chain.wait.for_receipt(cancel_txn_h)

    assert web3.eth.getBalance(canary.address) == 0
    # ensure it also cancells the pending call contract
    assert fbc.call().isCancelled() is True
