import pytest
from web3.utils.encoding import decode_hex


def test_execution_rejected_for_insufficient_gas(chain,
                                                 RequestData,
                                                 proxy,
                                                 txn_recorder,
                                                 request_lib,
                                                 get_execute_data,
                                                 get_abort_data,
                                                 AbortReasons):
    txn_request = RequestData(
        toAddress=txn_recorder.address,
        callGas=100000,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    assert txn_recorder.call().wasCalled() is False

    chain.wait.for_block(request_data.schedule.windowStart)

    minimum_call_gas = request_data.txnData.callGas + request_lib.call().GAS_TO_AUTHORIZE_EXECUTION() + request_lib.call().GAS_TO_COMPLETE_EXECUTION()

    call_data_hex = txn_request._encode_transaction_data('execute')
    execute_txn_hash = proxy.transact().__proxy(
        to=txn_request.address,
        callData=decode_hex(call_data_hex),
        callGas=minimum_call_gas - 1,
    )
    chain.wait.for_receipt(execute_txn_hash)

    with pytest.raises(AssertionError):
        get_execute_data(execute_txn_hash)

    abort_data = get_abort_data(execute_txn_hash)
    reasons = {entry['args']['reason'] for entry in abort_data}
    assert AbortReasons.InsufficientGas in reasons


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

    execute_txn_hash = txn_request.transact().execute()
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

    cancel_txn_hash = txn_request.transact().cancel()
    chain.wait.for_receipt(cancel_txn_hash)

    request_data.refresh()
    assert request_data.meta.isCancelled is True

    chain.wait.for_block(request_data.schedule.windowStart)

    execute_txn_hash = txn_request.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert txn_recorder.call().wasCalled() is False
    assert request_data.meta.wasCalled is False

    with pytest.raises(AssertionError):
        get_execute_data(execute_txn_hash)

    abort_data = get_abort_data(execute_txn_hash)
    reasons = {entry['args']['reason'] for entry in abort_data}
    assert AbortReasons.WasCancelled in reasons


def test_execution_rejected_if_before_call_window(chain,
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

    execute_txn_hash = txn_request.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert txn_recorder.call().wasCalled() is False
    assert request_data.meta.wasCalled is False

    with pytest.raises(AssertionError):
        get_execute_data(execute_txn_hash)

    abort_data = get_abort_data(execute_txn_hash)
    reasons = {entry['args']['reason'] for entry in abort_data}
    assert AbortReasons.BeforeCallWindow in reasons


def test_execution_rejected_if_after_call_window(chain,
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

    chain.wait.for_block(request_data.schedule.windowStart + request_data.schedule.windowSize + 1)

    execute_txn_hash = txn_request.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert txn_recorder.call().wasCalled() is False
    assert request_data.meta.wasCalled is False

    with pytest.raises(AssertionError):
        get_execute_data(execute_txn_hash)

    abort_data = get_abort_data(execute_txn_hash)
    reasons = {entry['args']['reason'] for entry in abort_data}
    assert AbortReasons.AfterCallWindow in reasons


def test_execution_rejected_if_claimed_by_other(chain,
                                                web3,
                                                RequestData,
                                                txn_recorder,
                                                get_execute_data,
                                                get_abort_data,
                                                AbortReasons):
    assert False


def test_execution_rejected_if_stack_too_deep(chain,
                                              web3,
                                              RequestData,
                                              txn_recorder,
                                              get_execute_data,
                                              get_abort_data,
                                              AbortReasons):
    assert False
