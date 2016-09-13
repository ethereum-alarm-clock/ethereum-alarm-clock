import gevent


def test_canary_returns_funds_when_exhausted(chain, web3, denoms,
                                             deploy_canary, FutureBlockCall):
    endowment = web3.toWei('4.003', 'ether')

    scheduler = chain.get_contract('Scheduler')
    canary = deploy_canary(endowment=endowment, deploy_from=web3.eth.accounts[1])

    initial_balance = web3.eth.getBalance(canary.address)
    assert initial_balance == endowment

    assert canary.call().isAlive() is False

    init_txn_h = canary.transact().initialize()
    chain.wait.for_receipt(init_txn_h)

    assert canary.call().isAlive() is True

    initial_owner_balance = web3.eth.getBalance(web3.eth.accounts[1])

    with gevent.Timeout(180):
        while web3.eth.getBalance(canary.address) > 0 or canary.call().isAlive():
            fbc_address = canary.call().callContractAddress()

            assert scheduler.call().isKnownCall(fbc_address) is True

            fbc = FutureBlockCall(address=fbc_address)
            chain.wait.for_block(fbc.call().targetBlock())

            exec_txn_h = fbc.transact().execute()
            chain.wait.for_receipt(exec_txn_h)

            assert fbc.call().wasCalled()

    assert canary.call().isAlive() is False
    assert web3.eth.getBalance(canary.address) == 0

    after_owner_balance = web3.eth.getBalance(web3.eth.accounts[1])

    assert after_owner_balance > initial_owner_balance
