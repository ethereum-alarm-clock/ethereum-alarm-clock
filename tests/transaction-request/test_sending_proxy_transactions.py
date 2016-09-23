def test_cannot_send_proxy_transaction_before_end_of_execution_window(chain,
                                                                      web3,
                                                                      RequestData,
                                                                      txn_recorder):
    txn_request = RequestData(
        toAddress=txn_recorder.address,
        windowStart=web3.eth.blockNumber + 255 + 10 + 5,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    def assert_recorder_empty():
        assert txn_recorder.call().wasCalled() is False
        assert txn_recorder.call().lastCaller() == '0x0000000000000000000000000000000000000000'
        assert txn_recorder.call().lastCallValue() == 0
        assert txn_recorder.call().lastCallGas() == 0
        assert txn_recorder.call().lastCallData() == ''

    # ensure it starts empty.
    assert_recorder_empty()

    # test before claim window
    chain.wait.for_receipt(
        txn_request.transact().sendProxyTransaction(txn_recorder.address, 100000, 0, 'some-call-data')
    )
    assert_recorder_empty()

    # fastforward to claim window.
    chain.wait.for_block(request_data.schedule.windowStart - 10 - 200)

    # test during claim window
    chain.wait.for_receipt(
        txn_request.transact().sendProxyTransaction(txn_recorder.address, 100000, 0, 'some-call-data')
    )
    assert_recorder_empty()

    # fastforward to freeze window.
    chain.wait.for_block(request_data.schedule.windowStart - 9)

    # test during claim window
    chain.wait.for_receipt(
        txn_request.transact().sendProxyTransaction(txn_recorder.address, 100000, 0, 'some-call-data')
    )
    assert_recorder_empty()

    # fastforward to during execution window
    chain.wait.for_block(request_data.schedule.windowStart + 10)

    # test during claim window
    chain.wait.for_receipt(
        txn_request.transact().sendProxyTransaction(txn_recorder.address, 100000, 0, 'some-call-data')
    )
    assert_recorder_empty()

    # Now execute the transaction
    chain.wait.for_receipt(txn_request.transact().execute())
    request_data.refresh()

    assert request_data.meta.wasCalled

    # reset the recorder.
    chain.wait.for_receipt(txn_recorder.transact().__reset__())
    assert_recorder_empty()


def test_can_send_proxy_transaction_after_execution_window(chain, RequestData, txn_recorder):
    txn_request = RequestData(
        toAddress=txn_recorder.address,
    ).direct_deploy()
    request_data = RequestData.from_contract(txn_request)

    chain.wait.for_block(request_data.schedule.windowStart + request_data.schedule.windowSize + 5)

    assert txn_recorder.call().wasCalled() is False
    assert txn_recorder.call().lastCaller() == '0x0000000000000000000000000000000000000000'
    assert txn_recorder.call().lastCallValue() == 0
    assert txn_recorder.call().lastCallGas() == 0
    assert txn_recorder.call().lastCallData() == ''

    chain.wait.for_receipt(
        txn_request.transact().sendProxyTransaction(txn_recorder.address, 500000, 0, 'some-call-data')
    )

    assert txn_recorder.call().wasCalled() is True
    assert txn_recorder.call().lastCaller() == txn_request.address
    assert txn_recorder.call().lastCallValue() == 0
    assert txn_recorder.call().lastCallData().startswith('some-call-data')
    assert len(txn_recorder.call().lastCallData()) == 32

    call_gas_delta = abs(txn_recorder.call().lastCallGas() - 500000)
    assert call_gas_delta < 10000
