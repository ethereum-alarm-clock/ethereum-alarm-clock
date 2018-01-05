import pytest


DAY = 60 * 60 * 24


def test_cannot_claim_before_first_claim_timestamp(chain,
                                                   web3,
                                                   RequestData,
                                                   set_timestamp,
                                                   get_claim_data):
    window_start = web3.eth.getBlock('latest')['timestamp'] + DAY
    txn_request = RequestData(
        temporalUnit=2,
        windowStart=window_start,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    first_claim_timestamp = request_data.schedule.windowStart - request_data.schedule.freezePeriod - request_data.schedule.claimWindowSize

    # sanity
    assert first_claim_timestamp > web3.eth.getBlock('latest')['timestamp']

    set_timestamp(first_claim_timestamp - 10)

    claim_txn_hash = txn_request.transact({
        'value': 2 * request_data.paymentData.payment,
    }).claim()
    chain.wait.for_receipt(claim_txn_hash)

    with pytest.raises(AssertionError):
        get_claim_data(claim_txn_hash)

    request_data.refresh()
    assert request_data.claimData.claimedBy == '0x0000000000000000000000000000000000000000'


def test_can_claim_at_first_claim_timestamp(chain,
                                            web3,
                                            RequestData,
                                            set_timestamp,
                                            get_claim_data):
    window_start = web3.eth.getBlock('latest')['timestamp'] + DAY
    txn_request = RequestData(
        temporalUnit=2,
        windowStart=window_start,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    first_claim_timestamp = request_data.schedule.windowStart - request_data.schedule.freezePeriod - request_data.schedule.claimWindowSize

    # sanity
    assert first_claim_timestamp > web3.eth.getBlock('latest')['timestamp']

    set_timestamp(first_claim_timestamp)

    claim_txn_hash = txn_request.transact({
        'value': 2 * request_data.paymentData.payment,
    }).claim()
    chain.wait.for_receipt(claim_txn_hash)

    claim_data = get_claim_data(claim_txn_hash)
    assert claim_data

    request_data.refresh()
    assert request_data.claimData.claimedBy == web3.eth.coinbase


def test_can_claim_at_last_claim_timestamp(chain,
                                           web3,
                                           set_timestamp,
                                           RequestData):
    window_start = web3.eth.getBlock('latest')['timestamp'] + DAY
    txn_request = RequestData(
        temporalUnit=2,
        windowStart=window_start,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    last_claim_timestamp = request_data.schedule.windowStart - request_data.schedule.freezePeriod

    # sanity
    assert last_claim_timestamp > web3.eth.getBlock('latest')['timestamp']

    set_timestamp(last_claim_timestamp - 17)

    claim_txn_hash = txn_request.transact({
        'value': 2 * request_data.paymentData.payment,
    }).claim()
    chain.wait.for_receipt(claim_txn_hash)

    request_data.refresh()
    assert request_data.claimData.claimedBy == web3.eth.coinbase


def test_cannot_claim_after_last_claim_timestamp(chain,
                                                 web3,
                                                 RequestData,
                                                 set_timestamp,
                                                 get_claim_data):
    window_start = web3.eth.getBlock('latest')['timestamp'] + DAY
    txn_request = RequestData(
        temporalUnit=2,
        windowStart=window_start,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    last_claim_timestamp = request_data.schedule.windowStart - request_data.schedule.freezePeriod

    # sanity
    assert last_claim_timestamp > web3.eth.getBlock('latest')['timestamp']

    set_timestamp(last_claim_timestamp + 1)

    claim_txn_hash = txn_request.transact({
        'value': 2 * request_data.paymentData.payment,
    }).claim()
    chain.wait.for_receipt(claim_txn_hash)

    with pytest.raises(AssertionError):
        get_claim_data(claim_txn_hash)

    request_data.refresh()
    assert request_data.claimData.claimedBy == '0x0000000000000000000000000000000000000000'


def test_executing_own_claimed_timestamp_based_request(chain,
                                                       web3,
                                                       RequestData,
                                                       get_execute_data,
                                                       set_timestamp,
                                                       get_claim_data):
    window_start = web3.eth.getBlock('latest')['timestamp'] + DAY
    txn_request = RequestData(
        temporalUnit=2,
        windowStart=window_start,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    first_claim_timestamp = request_data.schedule.windowStart - request_data.schedule.freezePeriod - request_data.schedule.claimWindowSize

    # sanity
    assert first_claim_timestamp > web3.eth.getBlock('latest')['timestamp']

    set_timestamp(first_claim_timestamp)

    claim_txn_hash = txn_request.transact({
        'value': 2 * request_data.paymentData.payment,
        'from': web3.eth.accounts[1],
    }).claim()
    chain.wait.for_receipt(claim_txn_hash)

    request_data.refresh()
    assert request_data.claimData.claimedBy == web3.eth.accounts[1]

    assert get_claim_data(claim_txn_hash)

    set_timestamp(request_data.schedule.windowStart)

    execute_txn_hash = txn_request.transact({
        'from': web3.eth.accounts[1],
        'gas': 3000000,
    }).execute()
    chain.wait.for_receipt(execute_txn_hash)

    request_data.refresh()
    assert request_data.meta.wasCalled is True

    assert get_execute_data(execute_txn_hash)


def test_executing_other_claimed_call_after_timestamp_reserved_window(chain,
                                                                      web3,
                                                                      RequestData,
                                                                      set_timestamp,
                                                                      get_claim_data,
                                                                      get_execute_data):
    window_start = web3.eth.getBlock('latest')['timestamp'] + DAY
    txn_request = RequestData(
        temporalUnit=2,
        windowStart=window_start,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    first_claim_timestamp = request_data.schedule.windowStart - request_data.schedule.freezePeriod - request_data.schedule.claimWindowSize

    # sanity
    assert first_claim_timestamp > web3.eth.getBlock('latest')['timestamp']

    set_timestamp(first_claim_timestamp)

    claim_txn_hash = txn_request.transact({
        'value': 2 * request_data.paymentData.payment,
        'from': web3.eth.accounts[1],
    }).claim()
    chain.wait.for_receipt(claim_txn_hash)

    request_data.refresh()
    assert request_data.claimData.claimedBy == web3.eth.accounts[1]

    assert get_claim_data(claim_txn_hash)

    set_timestamp(
        request_data.schedule.windowStart + request_data.schedule.reservedWindowSize
    )

    execute_txn_hash = txn_request.transact({'gas': 3000000}).execute()
    chain.wait.for_receipt(execute_txn_hash)

    request_data.refresh()
    assert request_data.meta.wasCalled is True

    assert get_execute_data(execute_txn_hash)


def test_claim_timestamp_determines_payment_amount(chain,
                                                   web3,
                                                   set_timestamp,
                                                   RequestData):
    window_start = web3.eth.getBlock('latest')['timestamp'] + DAY
    txn_request = RequestData(
        temporalUnit=2,
        windowStart=window_start,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    claim_at = request_data.schedule.windowStart - request_data.schedule.freezePeriod - request_data.schedule.claimWindowSize + request_data.schedule.claimWindowSize * 2 // 3

    expected_payment_modifier = 100 * 2 // 3

    # sanity
    assert request_data.claimData.paymentModifier == 0
    assert claim_at > web3.eth.getBlock('latest')['timestamp']

    set_timestamp(claim_at)

    claim_txn_hash = txn_request.transact({
        'value': 2 * request_data.paymentData.payment,
    }).claim()
    chain.wait.for_receipt(claim_txn_hash)

    request_data.refresh()
    assert request_data.claimData.paymentModifier == expected_payment_modifier
