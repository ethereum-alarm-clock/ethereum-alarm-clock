from web3.utils.encoding import decode_hex


def test_txn_request_payments(chain,
                              web3,
                              get_execute_data,
                              RequestData):
    txn_request = RequestData(donation=12345).direct_deploy()
    request_data = RequestData.from_contract(txn_request)
    assert request_data.paymentData.donation == 12345

    before_donation_balance = web3.eth.getBalance(request_data.paymentData.donationBenefactor)
    before_payment_balance = web3.eth.getBalance(web3.eth.accounts[1])

    chain.wait.for_block(request_data.schedule.windowStart)

    execute_txn_hash = txn_request.transact({'from': web3.eth.accounts[1]}).execute()
    execute_txn = web3.eth.getTransaction(execute_txn_hash)
    execute_txn_receipt = chain.wait.for_receipt(execute_txn_hash)

    execute_data = get_execute_data(execute_txn_hash)

    after_donation_balance = web3.eth.getBalance(request_data.paymentData.donationBenefactor)
    after_payment_balance = web3.eth.getBalance(web3.eth.accounts[1])

    donation = execute_data['args']['donation']
    assert donation == 12345
    assert after_donation_balance - before_donation_balance == donation

    payment = execute_data['args']['payment']

    gas_price = execute_txn['gasPrice']
    gas_used = execute_txn_receipt['gasUsed']
    gas_cost = gas_used * gas_price

    expected_payment = gas_cost + request_data.paymentData.payment

    assert payment >= expected_payment
    assert payment - expected_payment < 120000 * gas_price

    assert after_payment_balance - before_payment_balance == payment - gas_cost


def test_txn_request_payments_when_claimed(chain, web3, get_execute_data, RequestData):
    txn_request = RequestData(donation=12345, windowStart=web3.eth.blockNumber + 10 + 255 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    before_payment_balance = web3.eth.getBalance(web3.eth.accounts[1])

    claim_at = request_data.schedule.windowStart - request_data.schedule.freezePeriod - 5

    assert claim_at > web3.eth.blockNumber

    chain.wait.for_block(claim_at)

    claim_deposit = 2 * request_data.paymentData.payment
    assert claim_deposit > 0

    claim_txn_hash = txn_request.transact({
        'value': claim_deposit,
        'from': web3.eth.accounts[1],
    }).claim()
    claim_txn = web3.eth.getTransaction(claim_txn_hash)
    claim_txn_receipt = chain.wait.for_receipt(claim_txn_hash)
    claim_gas_cost = claim_txn['gasPrice'] * claim_txn_receipt['gasUsed']

    after_claim_balance = web3.eth.getBalance(web3.eth.accounts[1])
    assert before_payment_balance - after_claim_balance == claim_deposit + claim_gas_cost

    request_data.refresh()

    assert request_data.claimData.claimedBy == web3.eth.accounts[1]

    chain.wait.for_block(request_data.schedule.windowStart)

    execute_txn_hash = txn_request.transact({'from': web3.eth.accounts[1]}).execute()
    execute_txn = web3.eth.getTransaction(execute_txn_hash)
    execute_txn_receipt = chain.wait.for_receipt(execute_txn_hash)

    request_data.refresh()

    execute_data = get_execute_data(execute_txn_hash)

    after_payment_balance = web3.eth.getBalance(web3.eth.accounts[1])

    payment = execute_data['args']['payment']

    gas_price = execute_txn['gasPrice']
    gas_used = execute_txn_receipt['gasUsed']
    gas_cost = gas_used * gas_price

    expected_payment = claim_deposit + gas_cost + request_data.claimData.paymentModifier * request_data.paymentData.payment // 100

    assert payment >= expected_payment
    assert payment - expected_payment < 100000 * gas_price

    assert after_payment_balance - before_payment_balance == payment - claim_deposit - gas_cost - claim_gas_cost


def test_accounting_when_everything_throws(chain,
                                           web3,
                                           get_execute_data,
                                           RequestData,
                                           error_generator):
    txn_request = RequestData(
        createdBy=error_generator.address,
        owner=error_generator.address,
        donationBenefactor=error_generator.address,
        toAddress=error_generator.address,
        callData=decode_hex(error_generator._encode_transaction_data('doThrow')),
        windowStart=web3.eth.blockNumber + 10 + 255 + 5,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    claim_at = request_data.schedule.windowStart - 10 - 5
    deposit_amount = request_data.paymentData.payment * 2

    assert claim_at > web3.eth.blockNumber

    chain.wait.for_block(claim_at)

    claim_call_data = decode_hex(txn_request._encode_transaction_data('claim'))
    claim_txn_hash = error_generator.transact({
        'value': deposit_amount,
    }).__proxy(txn_request.address, claim_call_data, )
    chain.wait.for_receipt(claim_txn_hash)

    chain.wait.for_block(request_data.schedule.windowStart)

    execute_call_data = decode_hex(txn_request._encode_transaction_data('execute'))

    execute_txn_hash = error_generator.transact({'from': web3.eth.accounts[1]}).__proxy(
        to=txn_request.address,
        callData=execute_call_data,
    )
    execute_txn_receipt = chain.wait.for_receipt(execute_txn_hash)

    chain.wait.for_block(request_data.schedule.windowStart + request_data.schedule.windowSize)

    execute_data = get_execute_data(execute_txn_hash)
    request_data.refresh()

    assert request_data.meta.wasCalled is True
    assert request_data.meta.wasSuccessful is False

    gas_used = execute_txn_receipt['gasUsed']
    measured_gas_consumption = execute_data['args']['measuredGasConsumption']

    assert measured_gas_consumption > gas_used
    assert measured_gas_consumption - gas_used < 50000

    payment_owed = request_data.paymentData.paymentOwed
    donation_owed = request_data.paymentData.donationOwed

    assert payment_owed > 0
    assert payment_owed == execute_data['args']['payment']
    assert donation_owed > 0
    assert donation_owed == execute_data['args']['donation']

    # make the contract stop throwing now.
    chain.wait.for_receipt(error_generator.transact().toggle())
    assert error_generator.call().shouldThrow() is False

    before_payments_contract_balance = web3.eth.getBalance(txn_request.address)

    before_owner_refund_balance = web3.eth.getBalance(error_generator.address)

    issue_owner_refund_txn_hash = txn_request.transact().sendOwnerEther()
    chain.wait.for_receipt(issue_owner_refund_txn_hash)

    after_owner_refund_balance = web3.eth.getBalance(error_generator.address)
    owner_refund = after_owner_refund_balance - before_owner_refund_balance
    assert owner_refund > 0

    before_payment_balance = web3.eth.getBalance(error_generator.address)

    issue_payment_txn_hash = txn_request.transact().sendPayment()
    chain.wait.for_receipt(issue_payment_txn_hash)
    request_data.refresh()

    after_payment_balance = web3.eth.getBalance(error_generator.address)
    assert after_payment_balance - before_payment_balance == payment_owed

    before_donation_balance = web3.eth.getBalance(error_generator.address)

    issue_donation_txn_hash = txn_request.transact().sendDonation()
    chain.wait.for_receipt(issue_donation_txn_hash)
    request_data.refresh()

    after_donation_balance = web3.eth.getBalance(error_generator.address)
    assert after_donation_balance - before_donation_balance == donation_owed

    assert owner_refund + payment_owed + donation_owed == before_payments_contract_balance
