def test_late_claim_decreases_default_payment(chain, web3, denoms,
                                              get_scheduled_fbc,
                                              get_4byte_selector):
    scheduler = chain.get_contract('Scheduler')
    client_contract = chain.get_contract('TestCallExecution')

    target_block = web3.eth.blockNumber + 300

    noop_4byte_selector = get_4byte_selector(client_contract, 'noop')

    scheduling_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleCall(
        contractAddress=client_contract.address,
        abiSignature=noop_4byte_selector,
        targetBlock=target_block,
    )

    fbc = get_scheduled_fbc(scheduling_txn_hash)

    chain.wait.for_block(fbc.call().maxClaimBlock())

    claim_txn_hash = fbc.transact({'value': 10 * denoms.ether}).claim()
    chain.wait.for_receipt(claim_txn_hash)

    assert fbc.call().claimer() == web3.eth.coinbase

    chain.wait.for_block(target_block)

    default_payment_before = scheduler.call().defaultPayment()

    execute_txn_hash = fbc.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert fbc.call().wasCalled()

    expected = default_payment_before * 10001 // 10000
    actual = scheduler.call().defaultPayment()

    assert actual > default_payment_before
    assert actual == expected
