import pytest


def test_execution_rejected_if_claimed_by_other_for_timestamp(chain,
                                                              web3,
                                                              RequestData,
                                                              txn_recorder,
                                                              get_execute_data,
                                                              set_timestamp,
                                                              get_abort_data,
                                                              AbortReasons):
    window_start = web3.eth.getBlock('latest')['timestamp'] + 60 * 60 * 24
    txn_request = RequestData(
        windowStart=window_start,
        toAddress=txn_recorder.address,
        temporalUnit=2,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    claim_at = request_data.schedule.windowStart - request_data.schedule.freezePeriod - 60
    set_timestamp(claim_at)

    txn_request.transact({
        'from': web3.eth.accounts[1],
        'value': 2 * request_data.paymentData.payment,
    }).claim()

    request_data.refresh()
    assert request_data.claimData.claimedBy == web3.eth.accounts[1]

    set_timestamp(request_data.schedule.windowStart)

    assert txn_recorder.call().wasCalled() is False
    assert request_data.meta.wasCalled is False

    execute_txn_hash = txn_request.transact({'gas': 3000000}).execute()
    chain.wait.for_receipt(execute_txn_hash)

    request_data.refresh()

    assert txn_recorder.call().wasCalled() is False
    assert request_data.meta.wasCalled is False

    with pytest.raises(AssertionError):
        get_execute_data(execute_txn_hash)

    abort_data = get_abort_data(execute_txn_hash)
    reasons = {entry['args']['reason'] for entry in abort_data}
    assert AbortReasons.ReservedForClaimer in reasons
