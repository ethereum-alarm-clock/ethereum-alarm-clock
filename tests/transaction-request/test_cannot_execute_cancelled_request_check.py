import pytest


def test_execution_rejected_if_cancelled(chain,
                                         web3,
                                         RequestData,
                                         txn_recorder,
                                         get_execute_data,
                                         get_abort_data,
                                         AbortReasons):
    txn_request = RequestData(
        toAddress=txn_recorder.address,
        windowStart=web3.eth.blockNumber + 20,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    assert txn_recorder.call().wasCalled() is False
    assert request_data.meta.wasCalled is False
    assert request_data.meta.isCancelled is False

    cancel_txn_hash = txn_request.transact({'gas': 3000000}).cancel()
    chain.wait.for_receipt(cancel_txn_hash)

    request_data.refresh()
    assert request_data.meta.isCancelled is True

    chain.wait.for_block(request_data.schedule.windowStart)

    execute_txn_hash = txn_request.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    request_data.refresh()

    assert txn_recorder.call().wasCalled() is False
    assert request_data.meta.wasCalled is False

    with pytest.raises(AssertionError):
        get_execute_data(execute_txn_hash)

    abort_data = get_abort_data(execute_txn_hash)
    reasons = {entry['args']['reason'] for entry in abort_data}
    assert AbortReasons.WasCancelled in reasons
