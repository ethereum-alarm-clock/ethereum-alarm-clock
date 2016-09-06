

def test_early_claim_decreases_default_payment(chain,
                                               web3,
                                               denoms,
                                               deploy_fbc):
    scheduler = chain.get_contract('Scheduler')
    client_contract = chain.get_contract('TestCallExecution')

    target_block = web3.eth.blockNumber + 300

    fbc = deploy_fbc(
        contract=client_contract,
        method_name='noop',
        target_block=web3.eth.blockNumber + 300,
        payment=12345,
        donation=54321,
    )

    chain.wait.for_block(fbc.call().firstClaimBlock())

    claim_txn_hash = fbc.transact({'value': 10 * denoms.ether}).claim()
    chain.wait.for_receipt(claim_txn_hash)

    assert fbc.call().claimer() == web3.eth.coinbase

    chain.wait.for_block(target_block)

    default_payment_before = scheduler.call().defaultPayment()

    execute_txn_hash = fbc.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert fbc.call().wasCalled()

    expected = default_payment_before * 9999 / 10000
    actual = scheduler.call().defaultPayment()

    assert actual < default_payment_before
    assert actual == expected
