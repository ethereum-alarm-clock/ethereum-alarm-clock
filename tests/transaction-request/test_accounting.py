def test_txn_request_payments(chain,
                              web3,
                              get_execute_data,
                              RequestData):
    txn_request = RequestData(donation=12345).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    before_donation_balance = web3.eth.getBalance(request_data.paymentData.donationBenefactor)

    chain.wait.for_block(request_data.schedule.windowStart)

    execute_txn_hash = txn_request.transact({'from': web3.eth.accounts[1]}).execute()
    execute_txn = web3.eth.getTransaction(execute_txn_hash)
    execute_txn_receipt = chain.wait.for_receipt(execute_txn_hash)

    execute_data = get_execute_data(execute_txn_hash)

    after_donation_balance = web3.eth.getBalance(request_data.paymentData.donationBenefactor)

    donation = execute_data['args']['donation']
    assert donation == 12345
    assert after_donation_balance - before_donation_balance == donation

    payment = execute_data['args']['payment']

    gas_price = execute_txn['gasPrice']
    gas_used = execute_txn_receipt['gasUsed']
    gas_cost = gas_used * gas_price

    expected_payment = gas_cost + request_data.paymentData.payment

    assert payment >= expected_payment
