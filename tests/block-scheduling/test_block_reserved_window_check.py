import pytest


def test_execution_rejected_if_claimed_by_other_for_blocks(chain,
                                                           web3,
                                                           RequestData,
                                                           txn_recorder,
                                                           get_execute_data,
                                                           get_abort_data,
                                                           AbortReasons):
    txn_request = RequestData(
        windowStart=web3.eth.blockNumber + 255 + 10 + 5,
        toAddress=txn_recorder.address,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    claim_at = request_data.schedule.windowStart - request_data.schedule.freezePeriod - 10
    chain.wait.for_block(claim_at)

    txn_request.transact({
        'from': web3.eth.accounts[1],
        'value': 2 * request_data.paymentData.payment,
    }).claim()

    request_data.refresh()
    assert request_data.claimData.claimedBy == web3.eth.accounts[1]

    chain.wait.for_block(request_data.schedule.windowStart)

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
