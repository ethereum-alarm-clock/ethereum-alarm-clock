def test_request_factory(chain, web3, denoms):
    factory = chain.get_contract('RequestFactory')
    Request = chain.get_contract_factory('TransactionRequest')
    RequestLib = chain.get_contract_factory('RequestLib')

    chain_code = web3.eth.getCode(factory.address)
    assert len(chain_code) > 10

    window_start = web3.eth.blockNumber + 20

    create_txn_hash = factory.transact({
        'value': 10 * denoms.ether,
    }).createRequest(
        addressArgs=[
            '0xd3cda913deb6f67967b99d67acdfa1712c293601',
            web3.eth.coinbase,
        ],
        uintArgs=[
            255,  # claimWindowSize
            12345,  # donation
            54321,  # payment
            10,  # freezePeriod
            16,  # reservedWindowSize
            1,   # temporalUnit (blocks)
            window_start,  # windowStart
            255,  # windowSize
            1000000,  # callGas
            123456789,  # callValue
            0,  # requiredStackDepth
        ],
        callData='',
    )
    create_txn_receipt = chain.wait.for_receipt(create_txn_hash)

    request_created_filter = factory.pastEvents('RequestCreated')
    request_created_logs = request_created_filter.get()
    assert len(request_created_logs) == 1

    log_data = request_created_logs[0]

    request_address = log_data['args']['request']
    request = Request(address=request_address)

    chain.wait.for_block(window_start)

    #request_data = request.call().requestData()
    #request_call_data = request.call().callData()

    execute_txn_hash = request.transact({'gas': 3000000}).execute()
    execute_txn_receipt = chain.wait.for_receipt(execute_txn_hash)

    execute_filter = RequestLib.pastEvents('Executed', {
        'address': request.address,
    })
    execute_logs = execute_filter.get()
    assert len(execute_logs) == 1
    execute_data = execute_logs[0]

    benefactor_balance = web3.eth.getBalance('0xd3cda913deb6f67967b99d67acdfa1712c293601')
    assert False
