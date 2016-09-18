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
    assert claimed_request_data.claimData.claimedBy == web3.eth.coinbase

    cancel_txn_hash = txn_request.transact().cancel()
    chain.wait.for_receipt(cancel_txn_hash)

    updated_request_data = RequestData.from_contract(txn_request)
    assert updated_request_data.meta.isCancelled is False
