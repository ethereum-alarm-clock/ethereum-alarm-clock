def test_digger_proxy_works_as_expected(chain,
                                        web3,
                                        txn_recorder,
                                        digger_proxy):
    assert txn_recorder.call().wasCalled() is False

    dig_txn_hash = digger_proxy.transact().__dig_then_proxy(
        1023,
        txn_recorder.address,
        'the-call-data',
    )
    chain.wait.for_receipt(dig_txn_hash)

    assert txn_recorder.call().wasCalled() is True
    assert txn_recorder.call().lastCallData().startswith('the-call-data')


def test_digger_proxy_cannot_dig_past_1023(chain,
                                           web3,
                                           txn_recorder,
                                           digger_proxy):
    assert txn_recorder.call().wasCalled() is False

    dig_txn_hash = digger_proxy.transact().__dig_then_proxy(
        1024,
        txn_recorder.address,
        'the-call-data',
    )
    chain.wait.for_receipt(dig_txn_hash)

    assert txn_recorder.call().wasCalled() is False
