import pytest

from web3.utils.encoding import (
    decode_hex,
)


def test_execution_rejected_if_stack_too_deep(chain,
                                              web3,
                                              RequestData,
                                              txn_recorder,
                                              digger_proxy,
                                              get_execute_data,
                                              get_abort_data,
                                              AbortReasons):
    txn_request = RequestData(
        toAddress=txn_recorder.address,
        requiredStackDepth=1000,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    assert txn_recorder.call().wasCalled() is False
    assert request_data.meta.wasCalled is False
    assert request_data.txnData.requiredStackDepth == 1000

    chain.wait.for_block(request_data.schedule.windowStart)

    execute_call_data = decode_hex(txn_request._encode_transaction_data('execute'))

    execute_txn_hash = digger_proxy.transact({'gas': 3000000}).__dig_then_proxy(
        24,
        txn_request.address,
        execute_call_data,
    )
    chain.wait.for_receipt(execute_txn_hash)

    request_data.refresh()

    assert digger_proxy.call().result() is True
    assert txn_recorder.call().wasCalled() is False
    assert request_data.meta.wasCalled is False

    with pytest.raises(AssertionError):
        get_execute_data(execute_txn_hash)

    abort_data = get_abort_data(execute_txn_hash)
    reasons = {entry['args']['reason'] for entry in abort_data}
    assert AbortReasons.StackTooDeep in reasons


def test_execution_accepted_when_stack_extendable(chain,
                                                  web3,
                                                  RequestData,
                                                  txn_recorder,
                                                  digger_proxy,
                                                  get_execute_data,
                                                  get_abort_data,
                                                  AbortReasons):
    txn_request = RequestData(
        toAddress=txn_recorder.address,
        requiredStackDepth=1000,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    assert txn_recorder.call().wasCalled() is False
    assert request_data.meta.wasCalled is False
    assert request_data.txnData.requiredStackDepth == 1000

    chain.wait.for_block(request_data.schedule.windowStart)

    execute_call_data = decode_hex(txn_request._encode_transaction_data('execute'))

    execute_txn_hash = digger_proxy.transact({'gas': 3000000}).__dig_then_proxy(
        21,
        txn_request.address,
        execute_call_data,
    )
    chain.wait.for_receipt(execute_txn_hash)

    request_data.refresh()

    assert digger_proxy.call().result() is True
    assert txn_recorder.call().wasCalled() is True
    assert request_data.meta.wasCalled is True

    assert get_execute_data(execute_txn_hash)
