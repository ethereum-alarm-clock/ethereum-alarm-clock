def test_transaction_parameters(chain, RequestData, txn_recorder):
    txn_request = RequestData(
        toAddress=txn_recorder.address,
        callData='this-is-the-call-data',
        callGas=123456,
        callValue=121212,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    assert txn_recorder.call().wasCalled() is False
    assert txn_recorder.call().lastCaller() == '0x0000000000000000000000000000000000000000'
    assert txn_recorder.call().lastCallValue() == 0
    assert txn_recorder.call().lastCallGas() == 0
    assert txn_recorder.call().lastCallData() == ''

    chain.wait.for_block(request_data.schedule.windowStart)

    execute_txn_hash = txn_request.transact().execute()
    receipt = chain.wait.for_receipt(execute_txn_hash)
    print("Gas Used:", receipt['gasUsed'])

    assert txn_recorder.call().wasCalled() is True
    assert txn_recorder.call().lastCaller() == txn_request.address
    assert txn_recorder.call().lastCallValue() == 121212
    assert txn_recorder.call().lastCallData().startswith('this-is-the-call-data')
    assert len(txn_recorder.call().lastCallData()) == 32

    call_gas_delta = abs(txn_recorder.call().lastCallGas() - 123456)
    assert call_gas_delta < 10000
