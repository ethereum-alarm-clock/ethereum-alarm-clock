def test_request_factory_creates_request_with_provided_properties(chain,
                                                                  web3,
                                                                  denoms,
                                                                  request_factory,
                                                                  RequestData,
                                                                  get_txn_request):
    window_start = web3.eth.blockNumber + 20

    expected_request_data = RequestData(
        claimWindowSize=255,
        donation=12345,
        payment=54321,
        freezePeriod=10,
        windowStart=window_start,
        windowSize=255,
        reservedWindowSize=16,
        temporalUnit=1,
        callValue=123456789,
        callGas=1000000,
        requiredStackDepth=0
    )
    txn_request = expected_request_data.deploy_via_factory()

    actual_request_data = RequestData.from_contract(txn_request)

    assert actual_request_data.meta.owner == web3.eth.coinbase
    assert actual_request_data.meta.createdBy == web3.eth.coinbase
    assert actual_request_data.meta.isCancelled is False
    assert actual_request_data.meta.wasCalled is False
    assert actual_request_data.meta.wasSuccessful is False

    assert actual_request_data.claimData.claimedBy == '0x0000000000000000000000000000000000000000'
    assert actual_request_data.claimData.claimDeposit == 0
    assert actual_request_data.claimData.paymentModifier == 0

    assert actual_request_data.paymentData.donation == 12345
    assert actual_request_data.paymentData.donationBenefactor == '0xd3cda913deb6f67967b99d67acdfa1712c293601'
    assert actual_request_data.paymentData.donationOwed == 0
    assert actual_request_data.paymentData.payment == 54321
    assert actual_request_data.paymentData.paymentBenefactor == '0x0000000000000000000000000000000000000000'
    assert actual_request_data.paymentData.paymentOwed == 0

    assert actual_request_data.schedule.claimWindowSize == 255
    assert actual_request_data.schedule.freezePeriod == 10
    assert actual_request_data.schedule.windowStart == window_start
    assert actual_request_data.schedule.windowSize == 255
    assert actual_request_data.schedule.reservedWindowSize == 16
    assert actual_request_data.schedule.temporalUnit == 1

    assert actual_request_data.txnData.callData == ''
    assert actual_request_data.txnData.callValue == 123456789
    assert actual_request_data.txnData.callGas == 1000000
    assert actual_request_data.txnData.requiredStackDepth == 0
