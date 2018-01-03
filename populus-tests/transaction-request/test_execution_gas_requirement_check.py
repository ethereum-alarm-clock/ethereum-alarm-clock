import pytest

from web3.utils.encoding import (
    decode_hex,
)


def test_direct_execution_rejected_with_insufficient_gas(chain,
                                                         RequestData,
                                                         txn_recorder,
                                                         request_lib,
                                                         execution_lib,
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

    minimum_call_gas = (
        request_data.txnData.callGas +
        request_lib.call().EXECUTION_GAS_OVERHEAD()
    )
    too_low_call_gas = minimum_call_gas - request_lib.call().PRE_EXECUTION_GAS()

    execute_txn_hash = txn_request.transact({'gas': too_low_call_gas}).execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert txn_recorder.call().wasCalled() is False
    assert request_data.meta.wasCalled is False

    with pytest.raises(AssertionError):
        get_execute_data(execute_txn_hash)

    abort_data = get_abort_data(execute_txn_hash)
    reasons = {entry['args']['reason'] for entry in abort_data}
    assert AbortReasons.InsufficientGas in reasons


def test_direct_execution_accepted_with_minimum_gas(chain,
                                                    RequestData,
                                                    txn_recorder,
                                                    request_lib,
                                                    execution_lib,
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

    minimum_call_gas = (
        request_data.txnData.callGas +
        request_lib.call().EXECUTION_GAS_OVERHEAD()
    )

    execute_txn_hash = txn_request.transact({'gas': minimum_call_gas}).execute()
    chain.wait.for_receipt(execute_txn_hash)

    request_data.refresh()

    assert txn_recorder.call().wasCalled() is True
    assert request_data.meta.wasCalled is True

    assert get_execute_data(execute_txn_hash)


def test_proxy_execution_rejected_for_insufficient_gas(chain,
                                                       RequestData,
                                                       proxy,
                                                       txn_recorder,
                                                       request_lib,
                                                       execution_lib,
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

    minimum_call_gas = (
        request_data.txnData.callGas +
        request_lib.call().EXECUTION_GAS_OVERHEAD() +
        execution_lib.call().GAS_PER_DEPTH() * request_data.txnData.requiredStackDepth
    )
    too_low_call_gas = minimum_call_gas - request_lib.call().PRE_EXECUTION_GAS()

    call_data_hex = txn_request._encode_transaction_data('execute')
    execute_txn_hash = proxy.transact({'gas': 3000000}).__proxy(
        to=txn_request.address,
        callData=decode_hex(call_data_hex),
        callGas=too_low_call_gas,
    )
    chain.wait.for_receipt(execute_txn_hash)

    assert txn_recorder.call().wasCalled() is False
    assert request_data.meta.wasCalled is False

    with pytest.raises(AssertionError):
        get_execute_data(execute_txn_hash)

    abort_data = get_abort_data(execute_txn_hash)
    reasons = {entry['args']['reason'] for entry in abort_data}
    assert AbortReasons.InsufficientGas in reasons


def test_proxy_execution_accepted_at_minimum_gas(chain,
                                                 RequestData,
                                                 proxy,
                                                 txn_recorder,
                                                 request_lib,
                                                 execution_lib,
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

    minimum_call_gas = (
        request_data.txnData.callGas +
        request_lib.call().EXECUTION_GAS_OVERHEAD() +
        execution_lib.call().GAS_PER_DEPTH() * request_data.txnData.requiredStackDepth
    )

    call_data_hex = txn_request._encode_transaction_data('execute')
    execute_txn_hash = proxy.transact({'gas': 3000000}).__proxy(
        to=txn_request.address,
        callData=decode_hex(call_data_hex),
        callGas=minimum_call_gas,
    )
    chain.wait.for_receipt(execute_txn_hash)

    request_data.refresh()

    assert get_execute_data(execute_txn_hash)
    assert txn_recorder.call().wasCalled() is True
    assert request_data.meta.wasCalled is True
