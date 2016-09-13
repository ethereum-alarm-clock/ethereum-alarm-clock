def test_cannary_cannot_be_revived(chain, web3, deploy_canary, denoms,
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

    # Wait till after the call
    chain.wait.for_block(
        fbc.call().targetBlock() + fbc.call().gracePeriod() + 1
    )

    assert canary.call().isAlive() is False

    revive_txn_h = canary.transact().heartbeat()
    chain.wait.for_receipt(revive_txn_h)

    # shouldn't be alive.  stats shouldn't have changed
    assert canary.call().isAlive() is False
    assert canary.call().heartbeatCount() == 0
    assert canary.call().callContractAddress() == fbc_address
