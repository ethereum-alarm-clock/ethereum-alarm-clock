def test_execution_of_call_that_throws_exception(chain, deploy_fbc, CallLib):
    client_contract = chain.get_contract('TestErrors')

    fbc = deploy_fbc(client_contract, method_name='doFail')

    chain.wait.for_block(fbc.call().targetBlock())

    assert client_contract.call().value() is False

    execute_txn_hash = fbc.transact().execute()
    execute_txn_receipt = chain.wait.for_receipt(execute_txn_hash)

    assert client_contract.call().value() is False

    execute_filter = CallLib.pastEvents('CallExecuted', {
        'address': fbc.address,
        'fromBlock': execute_txn_receipt['blockNumber'],
        'toBlock': execute_txn_receipt['blockNumber'],
    })
    execute_logs = execute_filter.get()
    assert len(execute_logs) == 1
    execute_log_data = execute_logs[0]
    assert execute_log_data['args']['success'] is False
