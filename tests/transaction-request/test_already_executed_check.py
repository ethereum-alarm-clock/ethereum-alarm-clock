import pytest


def test_execution_rejected_if_already_executed(chain,
                                                RequestData,
                                                txn_recorder,
                                                get_execute_data,
                                                get_abort_data,
                                                AbortReasons):
    txn_request = RequestData(
        toAddress=txn_recorder.address,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    assert txn_recorder.call().wasCalled() is False
    assert request_data.meta.wasCalled is False

    chain.wait.for_block(request_data.schedule.windowStart)

    execute_txn_hash = txn_request.transact({'gas': 3000000}).execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert txn_recorder.call().wasCalled() is True
    request_data.refresh()
    assert request_data.meta.wasCalled is True

    duplicate_execute_txn_hash = txn_request.transact().execute()
    chain.wait.for_receipt(duplicate_execute_txn_hash)

    with pytest.raises(AssertionError):
        get_execute_data(duplicate_execute_txn_hash)

    abort_data = get_abort_data(duplicate_execute_txn_hash)
    reasons = {entry['args']['reason'] for entry in abort_data}
    assert AbortReasons.AlreadyCalled in reasons
