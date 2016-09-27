from web3.utils.encoding import decode_hex


def test_txn_request_for_txn_that_throw_exception(chain,
                                                  web3,
                                                  get_execute_data,
                                                  RequestData,
                                                  error_generator):
    txn_request = RequestData(
        createdBy=error_generator.address,
        donation=12345,
        toAddress=error_generator.address,
        callData=decode_hex(error_generator._encode_transaction_data('doThrow'))
    ).direct_deploy()

    request_data = RequestData.from_contract(txn_request)
    chain.wait.for_block(request_data.schedule.windowStart)

    execute_txn_hash = txn_request.transact({
        'from': web3.eth.accounts[1],
        'gas': 3000000,
    }).execute()
    execute_txn_receipt = chain.wait.for_receipt(execute_txn_hash)

    execute_data = get_execute_data(execute_txn_hash)
    request_data = RequestData.from_contract(txn_request)

    assert request_data.meta.wasCalled is True
    assert request_data.meta.wasSuccessful is False

    gas_used = execute_txn_receipt['gasUsed']
    measured_gas_consumption = execute_data['args']['measuredGasConsumption']

    assert measured_gas_consumption > gas_used
    assert measured_gas_consumption - gas_used < 120000


def test_txn_request_when_everything_throws(chain,
                                            web3,
                                            get_execute_data,
                                            RequestData,
                                            error_generator):
    txn_request = RequestData(
        createdBy=error_generator.address,
        owner=error_generator.address,
        donationBenefactor=error_generator.address,
        toAddress=error_generator.address,
        callData=decode_hex(error_generator._encode_transaction_data('doThrow'))
    ).direct_deploy()

    request_data = RequestData.from_contract(txn_request)
    chain.wait.for_block(request_data.schedule.windowStart)

    proxy_call_data = decode_hex(txn_request._encode_transaction_data('execute'))

    execute_txn_hash = error_generator.transact({
        'from': web3.eth.accounts[1],
        'gas': 3000000,
    }).__proxy(
        to=txn_request.address,
        callData=proxy_call_data,
    )
    execute_txn_receipt = chain.wait.for_receipt(execute_txn_hash)

    execute_data = get_execute_data(execute_txn_hash)
    request_data = RequestData.from_contract(txn_request)

    assert request_data.meta.wasCalled is True
    assert request_data.meta.wasSuccessful is False

    gas_used = execute_txn_receipt['gasUsed']
    measured_gas_consumption = execute_data['args']['measuredGasConsumption']

    assert measured_gas_consumption > gas_used
    assert measured_gas_consumption - gas_used < 50000
