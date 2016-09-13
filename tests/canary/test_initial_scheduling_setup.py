def test_canary_initialization(chain, web3, deploy_canary, denoms,
                               FutureBlockCall):
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

    # check that it has enough funds to successfully heartbeat
    assert web3.eth.getBalance(canary.address) >= 2 * denoms.ether

    fbc = FutureBlockCall(address=fbc_address)

    assert canary.call().isAlive() is True

    chain.wait.for_block(fbc.call().targetBlock())

    exec_txn_h = fbc.transact().execute()
    chain.wait.for_receipt(exec_txn_h)

    assert fbc.call().wasCalled()
    assert fbc.call().wasSuccessful()

    next_fbc_address = canary.call().callContractAddress()
    assert next_fbc_address != fbc_address
    assert scheduler.call().isKnownCall(fbc_address)

    assert canary.call().heartbeatCount() == 1
