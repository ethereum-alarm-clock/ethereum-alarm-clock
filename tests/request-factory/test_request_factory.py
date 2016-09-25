def test_request_factory_creates_request_with_provided_properties(chain,
                                                                  web3,
                                                                  denoms,
                                                                  txn_recorder,
                                                                  RequestData):
    request_lib = chain.get_contract('RequestLib')
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
    is_valid = request_lib.call().validate(
        endowment=10 * denoms.ether,
        **expected_request_data.to_init_kwargs()
    )
    assert all(is_valid)

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

    assert actual_request_data.txnData.toAddress == txn_recorder.address
    assert actual_request_data.txnData.callData == ''
    assert actual_request_data.txnData.callValue == 123456789
    assert actual_request_data.txnData.callGas == 1000000
    assert actual_request_data.txnData.requiredStackDepth == 0


def test_request_factory_insufficient_endowment_validation_error(chain,
                                                                 web3,
                                                                 denoms,
                                                                 txn_recorder,
                                                                 RequestData):
    request_lib = chain.get_contract('RequestLib')
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
    is_valid = request_lib.call().validate(
        endowment=123456789,  # too small of an endowment.
        **expected_request_data.to_init_kwargs()
    )
    assert not all(is_valid)
    assert is_valid[0] is False
    assert all(is_valid[1:])


def test_request_factory_too_large_reserved_window_validation_error(chain,
                                                                    web3,
                                                                    denoms,
                                                                    txn_recorder,
                                                                    RequestData):
    request_lib = chain.get_contract('RequestLib')
    window_start = web3.eth.blockNumber + 20

    expected_request_data = RequestData(
        claimWindowSize=255,
        donation=12345,
        payment=54321,
        freezePeriod=10,
        windowStart=window_start,
        windowSize=255,
        reservedWindowSize=255 + 1,  # 1 more than the window size.
        temporalUnit=1,
        callValue=123456789,
        callGas=1000000,
        requiredStackDepth=0
    )
    is_valid = request_lib.call().validate(
        endowment=10 * denoms.ether,
        **expected_request_data.to_init_kwargs()
    )
    assert not all(is_valid)
    assert is_valid[1] is False
    assert all(is_valid[:1])
    assert all(is_valid[2:])


def test_request_factory_invalid_temporal_unit_validation_error(chain,
                                                                web3,
                                                                denoms,
                                                                txn_recorder,
                                                                RequestData):
    request_lib = chain.get_contract('RequestLib')
    window_start = web3.eth.blockNumber + 20

    expected_request_data = RequestData(
        claimWindowSize=255,
        donation=12345,
        payment=54321,
        freezePeriod=10,
        windowStart=window_start,
        windowSize=255,
        reservedWindowSize=16,
        temporalUnit=3,  # Only 1, and 2 are supported.
        callValue=123456789,
        callGas=1000000,
        requiredStackDepth=0
    )
    is_valid = request_lib.call().validate(
        endowment=10 * denoms.ether,
        **expected_request_data.to_init_kwargs()
    )
    assert not all(is_valid)
    assert is_valid[2] is False
    assert all(is_valid[:2])
    assert all(is_valid[3:])


def test_request_factory_too_soon_execution_window_validation_error(chain,
                                                                    web3,
                                                                    denoms,
                                                                    txn_recorder,
                                                                    RequestData):
    request_lib = chain.get_contract('RequestLib')
    window_start = web3.eth.blockNumber + 10

    expected_request_data = RequestData(
        claimWindowSize=255,
        donation=12345,
        payment=54321,
        freezePeriod=11,  # more than the number of blocks between now and the windowStart.
        windowStart=window_start,
        windowSize=255,
        reservedWindowSize=16,
        temporalUnit=1,
        callValue=123456789,
        callGas=1000000,
        requiredStackDepth=0
    )
    is_valid = request_lib.call().validate(
        endowment=10 * denoms.ether,
        **expected_request_data.to_init_kwargs()
    )
    assert not all(is_valid)
    assert is_valid[3] is False
    assert all(is_valid[:3])
    assert all(is_valid[4:])


def test_request_factory_invalid_required_stack_depth_validation_error(chain,
                                                                       web3,
                                                                       denoms,
                                                                       txn_recorder,
                                                                       RequestData):
    request_lib = chain.get_contract('RequestLib')
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
        requiredStackDepth=1025,
    )
    is_valid = request_lib.call().validate(
        endowment=10 * denoms.ether,
        **expected_request_data.to_init_kwargs()
    )
    assert not all(is_valid)
    assert is_valid[4] is False
    assert all(is_valid[:4])
    assert all(is_valid[5:])


def test_request_factory_too_high_call_gas_validation_error(chain,
                                                            web3,
                                                            denoms,
                                                            txn_recorder,
                                                            RequestData):
    last_block = web3.eth.getBlock('latest')

    request_lib = chain.get_contract('RequestLib')
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
        callGas=last_block['gasLimit'],  # cannot be at gas limit.
        requiredStackDepth=0,
    )
    is_valid = request_lib.call().validate(
        endowment=10 * denoms.ether,
        **expected_request_data.to_init_kwargs()
    )
    assert not all(is_valid)
    assert is_valid[5] is False
    assert all(is_valid[:5])
    assert all(is_valid[6:])


def test_request_factory_to_address_as_null_validation_error(chain,
                                                             web3,
                                                             denoms,
                                                             txn_recorder,
                                                             RequestData):
    request_lib = chain.get_contract('RequestLib')
    window_start = web3.eth.blockNumber + 20

    expected_request_data = RequestData(
        toAddress='0x0000000000000000000000000000000000000000',  # cannot send to 0x0
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
        requiredStackDepth=0,
    )
    is_valid = request_lib.call().validate(
        endowment=10 * denoms.ether,
        **expected_request_data.to_init_kwargs()
    )
    assert not all(is_valid)
    assert is_valid[6] is False
    assert all(is_valid[:6])
