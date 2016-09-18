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

    cancel_txn_hash = txn_request.transact().cancel()
    chain.wait.for_receipt(cancel_txn_hash)

    updated_request_data = RequestData.from_contract(txn_request)
    assert updated_request_data.meta.isCancelled is False


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

    execute_txn_hash = txn_request.transact().execute()
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
