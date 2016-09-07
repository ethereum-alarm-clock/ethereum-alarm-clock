def test_unclaimed_call_does_not_change_default_payment(chain, web3, denoms,
                                                        get_scheduled_fbc,
                                                        get_4byte_selector):
    scheduler = chain.get_contract('Scheduler')
    client_contract = chain.get_contract('TestCallExecution')

    noop_4byte_selector = get_4byte_selector(client_contract, 'noop')

    scheduling_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleCall(
        contractAddress=client_contract.address,
        abiSignature=noop_4byte_selector,
    )

    fbc = get_scheduled_fbc(scheduling_txn_hash)

    chain.wait.for_block(fbc.call().targetBlock())

    default_payment_before = scheduler.call().defaultPayment()

    execute_txn_hash = fbc.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert fbc.call().wasCalled()
    assert scheduler.call().defaultPayment() == default_payment_before
