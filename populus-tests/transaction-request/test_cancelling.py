def test_cancelling_before_claim_window(chain, web3, RequestData):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    cancel_at = request_data.schedule.windowStart - request_data.schedule.freezePeriod - request_data.schedule.claimWindowSize - 3

    # sanity
    assert cancel_at > web3.eth.blockNumber
    assert request_data.meta.owner == web3.eth.coinbase
    assert request_data.meta.isCancelled is False

    chain.wait.for_block(cancel_at)

    cancel_txn_hash = txn_request.transact().cancel()
    chain.wait.for_receipt(cancel_txn_hash)

    updated_request_data = RequestData.from_contract(txn_request)
    assert updated_request_data.meta.isCancelled is True


def test_non_owner_cannot_cancel_before_claim_window(chain, web3, RequestData):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    cancel_at = request_data.schedule.windowStart - request_data.schedule.freezePeriod - request_data.schedule.claimWindowSize - 3

    # sanity
    assert cancel_at > web3.eth.blockNumber
    assert request_data.meta.owner == web3.eth.coinbase
    assert request_data.meta.isCancelled is False

    chain.wait.for_block(cancel_at)

    cancel_txn_hash = txn_request.transact({'from': web3.eth.accounts[1]}).cancel()
    chain.wait.for_receipt(cancel_txn_hash)

    updated_request_data = RequestData.from_contract(txn_request)
    assert updated_request_data.meta.isCancelled is False


def test_cancelling_during_claim_window_when_unclaimed(chain, web3, RequestData):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    cancel_at = request_data.schedule.windowStart - request_data.schedule.freezePeriod - 20

    # sanity
    assert cancel_at > web3.eth.blockNumber
    assert request_data.meta.owner == web3.eth.coinbase
    assert request_data.meta.isCancelled is False

    chain.wait.for_block(cancel_at)

    cancel_txn_hash = txn_request.transact().cancel()
    chain.wait.for_receipt(cancel_txn_hash)

    updated_request_data = RequestData.from_contract(txn_request)
    assert updated_request_data.meta.isCancelled is True


def test_not_cancellable_once_claimed(chain, web3, RequestData):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    cancel_at = request_data.schedule.windowStart - request_data.schedule.freezePeriod - 20
    claim_at = cancel_at - 5

    # sanity
    assert cancel_at > web3.eth.blockNumber
    assert request_data.meta.owner == web3.eth.coinbase
    assert request_data.meta.isCancelled is False

    chain.wait.for_block(claim_at)

    claim_txn_hash = txn_request.transact({
        'value': 2 * request_data.paymentData.payment,
        'from': web3.eth.accounts[1],
    }).claim()
    chain.wait.for_receipt(claim_txn_hash)

    claimed_request_data = RequestData.from_contract(txn_request)
    assert claimed_request_data.claimData.claimedBy == web3.eth.accounts[1]

    cancel_txn_hash = txn_request.transact().cancel()
    chain.wait.for_receipt(cancel_txn_hash)

    updated_request_data = RequestData.from_contract(txn_request)
    assert updated_request_data.meta.isCancelled is False


def test_not_cancellable_during_freeze_window(chain, web3, RequestData):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    cancel_at = request_data.schedule.windowStart - request_data.schedule.freezePeriod

    # sanity
    assert cancel_at > web3.eth.blockNumber
    assert request_data.meta.owner == web3.eth.coinbase
    assert request_data.meta.isCancelled is False

    chain.wait.for_block(cancel_at)

    cancel_txn_hash = txn_request.transact().cancel()
    chain.wait.for_receipt(cancel_txn_hash)

    request_data.refresh()
    assert request_data.meta.isCancelled is False


def test_not_cancellable_during_execution_window(chain, web3, RequestData):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    cancel_at = request_data.schedule.windowStart

    # sanity
    assert cancel_at > web3.eth.blockNumber
    assert request_data.meta.owner == web3.eth.coinbase
    assert request_data.meta.isCancelled is False

    chain.wait.for_block(cancel_at)

    cancel_txn_hash = txn_request.transact().cancel()
    chain.wait.for_receipt(cancel_txn_hash)

    updated_request_data = RequestData.from_contract(txn_request)
    assert updated_request_data.meta.isCancelled is False


def test_not_cancellable_if_was_called(chain, web3, RequestData):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    execute_at = request_data.schedule.windowStart
    cancel_at_first = request_data.schedule.windowStart + 10
    cancel_at_second = request_data.schedule.windowStart + request_data.schedule.windowSize + 5

    # sanity
    assert execute_at > web3.eth.blockNumber
    assert request_data.meta.owner == web3.eth.coinbase
    assert request_data.meta.isCancelled is False

    chain.wait.for_block(execute_at)

    execute_txn_hash = txn_request.transact({
        'gas': 3000000,
    }).execute()
    chain.wait.for_receipt(execute_txn_hash)

    after_execute_request_data = RequestData.from_contract(txn_request)
    assert after_execute_request_data.meta.wasCalled is True
    assert after_execute_request_data.meta.isCancelled is False

    chain.wait.for_block(cancel_at_first)

    first_cancel_txn_hash = txn_request.transact().cancel()
    chain.wait.for_receipt(first_cancel_txn_hash)

    after_first_cancel_request_data = RequestData.from_contract(txn_request)
    assert after_first_cancel_request_data.meta.isCancelled is False

    chain.wait.for_block(cancel_at_second)

    second_cancel_txn_hash = txn_request.transact().cancel()
    chain.wait.for_receipt(second_cancel_txn_hash)

    after_second_cancel_request_data = RequestData.from_contract(txn_request)
    assert after_second_cancel_request_data.meta.isCancelled is False


def test_cancellable_if_call_is_missed(chain, web3, RequestData):
    txn_request = RequestData(windowStart=web3.eth.blockNumber + 255 + 10 + 5).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    cancel_at = request_data.schedule.windowStart + request_data.schedule.windowSize + 10

    # sanity
    assert cancel_at > web3.eth.blockNumber
    assert request_data.meta.owner == web3.eth.coinbase
    assert request_data.meta.isCancelled is False

    chain.wait.for_block(cancel_at)

    cancel_txn_hash = txn_request.transact().cancel()
    chain.wait.for_receipt(cancel_txn_hash)

    updated_request_data = RequestData.from_contract(txn_request)
    assert updated_request_data.meta.isCancelled is True


def test_accounting_for_pre_execution_cancellation(chain,
                                                   web3,
                                                   denoms,
                                                   RequestData,
                                                   get_cancel_data):
    txn_request = RequestData(
        windowStart=web3.eth.blockNumber + 255 + 10 + 5,
        owner=web3.eth.accounts[1],
    ).direct_deploy({
        'from': web3.eth.accounts[1],
        'value': 10 * denoms.ether,
    })
    request_data = RequestData.from_contract(txn_request)

    cancel_at = request_data.schedule.windowStart - request_data.schedule.freezePeriod - 5

    # sanity
    assert cancel_at > web3.eth.blockNumber
    assert request_data.meta.owner == web3.eth.accounts[1]
    assert request_data.meta.isCancelled is False

    chain.wait.for_block(cancel_at)

    before_cancel_balance = web3.eth.getBalance(web3.eth.accounts[1])
    before_contract_balance = web3.eth.getBalance(txn_request.address)

    cancel_txn_hash = txn_request.transact({'from': web3.eth.accounts[1]}).cancel()
    cancel_txn_receipt = chain.wait.for_receipt(cancel_txn_hash)

    after_cancel_balance = web3.eth.getBalance(web3.eth.accounts[1])
    after_contract_balance = web3.eth.getBalance(txn_request.address)

    updated_request_data = RequestData.from_contract(txn_request)
    assert updated_request_data.meta.isCancelled is True

    cancel_data = get_cancel_data(cancel_txn_hash)
    # since this was cancelled by the owner.
    assert cancel_data['args']['rewardPayment'] == 0
    assert cancel_data['args']['measuredGasConsumption'] == 0

    assert before_contract_balance == 10 * denoms.ether
    assert after_contract_balance == 0

    assert after_cancel_balance - before_cancel_balance == 10 * denoms.ether - cancel_txn_receipt['gasUsed'] * web3.eth.gasPrice


def test_accounting_for_missed_execution_cancellation_by_owner(chain,
                                                               web3,
                                                               denoms,
                                                               RequestData,
                                                               get_cancel_data):
    txn_request = RequestData(
        windowStart=web3.eth.blockNumber + 255 + 10 + 5,
        owner=web3.eth.accounts[1],
    ).direct_deploy({
        'from': web3.eth.accounts[1],
        'value': 10 * denoms.ether,
    })
    request_data = RequestData.from_contract(txn_request)

    cancel_at = request_data.schedule.windowStart + request_data.schedule.windowSize + 1

    # sanity
    assert cancel_at > web3.eth.blockNumber
    assert request_data.meta.owner == web3.eth.accounts[1]
    assert request_data.meta.isCancelled is False

    chain.wait.for_block(cancel_at)

    before_cancel_balance = web3.eth.getBalance(web3.eth.accounts[1])
    before_contract_balance = web3.eth.getBalance(txn_request.address)

    cancel_txn_hash = txn_request.transact({'from': web3.eth.accounts[1]}).cancel()
    cancel_txn_receipt = chain.wait.for_receipt(cancel_txn_hash)

    after_cancel_balance = web3.eth.getBalance(web3.eth.accounts[1])
    after_contract_balance = web3.eth.getBalance(txn_request.address)

    updated_request_data = RequestData.from_contract(txn_request)
    assert updated_request_data.meta.isCancelled is True

    cancel_data = get_cancel_data(cancel_txn_hash)
    # since this was cancelled by the owner.
    assert cancel_data['args']['rewardPayment'] == 0
    assert cancel_data['args']['measuredGasConsumption'] == 0

    assert before_contract_balance == 10 * denoms.ether
    assert after_contract_balance == 0

    assert after_cancel_balance - before_cancel_balance == 10 * denoms.ether - cancel_txn_receipt['gasUsed'] * web3.eth.gasPrice


def test_accounting_for_missed_execution_cancellation_not_by_owner(chain,
                                                                   web3,
                                                                   denoms,
                                                                   RequestData,
                                                                   get_cancel_data):
    txn_request = RequestData(
        windowStart=web3.eth.blockNumber + 255 + 10 + 5,
        owner=web3.eth.coinbase,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    cancel_at = request_data.schedule.windowStart + request_data.schedule.windowSize + 1

    # sanity
    assert cancel_at > web3.eth.blockNumber
    assert request_data.meta.owner == web3.eth.coinbase
    assert request_data.meta.isCancelled is False

    chain.wait.for_block(cancel_at)

    before_cancel_balance = web3.eth.getBalance(web3.eth.accounts[1])
    before_contract_balance = web3.eth.getBalance(txn_request.address)

    cancel_txn_hash = txn_request.transact({'from': web3.eth.accounts[1]}).cancel()
    cancel_txn_receipt = chain.wait.for_receipt(cancel_txn_hash)

    after_cancel_balance = web3.eth.getBalance(web3.eth.accounts[1])
    after_contract_balance = web3.eth.getBalance(txn_request.address)

    updated_request_data = RequestData.from_contract(txn_request)
    assert updated_request_data.meta.isCancelled is True

    cancel_data = get_cancel_data(cancel_txn_hash)
    measured_gas_consumption = cancel_data['args']['measuredGasConsumption']
    assert measured_gas_consumption >= cancel_txn_receipt['gasUsed']

    assert cancel_data['args']['rewardPayment'] == measured_gas_consumption * web3.eth.gasPrice + updated_request_data.paymentData.payment // 100

    assert before_contract_balance == 10 * denoms.ether
    assert after_contract_balance == 0

    assert after_cancel_balance - before_cancel_balance == cancel_data['args']['rewardPayment'] - cancel_txn_receipt['gasUsed'] * web3.eth.gasPrice
