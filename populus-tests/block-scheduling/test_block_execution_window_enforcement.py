import pytest


def test_execution_rejected_if_before_execution_window_for_blocks(chain,
                                                                  web3,
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
    assert web3.eth.blockNumber < request_data.schedule.windowStart

    execute_txn_hash = txn_request.transact({'gas': 3000000}).execute()
    chain.wait.for_receipt(execute_txn_hash)

    request_data.refresh()

    assert txn_recorder.call().wasCalled() is False
    assert request_data.meta.wasCalled is False

    with pytest.raises(AssertionError):
        get_execute_data(execute_txn_hash)

    abort_data = get_abort_data(execute_txn_hash)
    reasons = {entry['args']['reason'] for entry in abort_data}
    assert AbortReasons.BeforeCallWindow in reasons


def test_execution_rejected_if_after_execution_window_for_blocks(chain,
                                                                 web3,
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

    end_execution_window = request_data.schedule.windowStart + request_data.schedule.windowSize
    chain.wait.for_block(end_execution_window + 1)

    assert web3.eth.blockNumber > end_execution_window

    execute_txn_hash = txn_request.transact({'gas': 3000000}).execute()
    chain.wait.for_receipt(execute_txn_hash)

    request_data.refresh()

    assert txn_recorder.call().wasCalled() is False
    assert request_data.meta.wasCalled is False

    with pytest.raises(AssertionError):
        get_execute_data(execute_txn_hash)

    abort_data = get_abort_data(execute_txn_hash)
    reasons = {entry['args']['reason'] for entry in abort_data}
    assert AbortReasons.AfterCallWindow in reasons


def test_execution_allowed_at_start_execution_window_for_blocks(chain,
                                                                web3,
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

    start_execution_window = request_data.schedule.windowStart
    chain.wait.for_block(start_execution_window)

    execute_txn_hash = txn_request.transact({'gas': 3000000}).execute()
    chain.wait.for_receipt(execute_txn_hash)

    request_data.refresh()

    assert txn_recorder.call().wasCalled() is True
    assert request_data.meta.wasCalled is True


def test_execution_allowed_at_end_execution_window_for_blocks(chain,
                                                              web3,
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

    end_execution_window = request_data.schedule.windowStart + request_data.schedule.windowSize
    chain.wait.for_block(end_execution_window)

    execute_txn_hash = txn_request.transact({'gas': 3000000}).execute()
    chain.wait.for_receipt(execute_txn_hash)

    request_data.refresh()

    assert txn_recorder.call().wasCalled() is True
    assert request_data.meta.wasCalled is True
