def test_gas_accounting_for_infinite_loop(unmigrated_chain, web3, deploy_fbc):
    chain = unmigrated_chain
    client_contract = chain.get_contract('TestErrors')
    CallLib = chain.get_contract_factory('CallLib')

    fbc = deploy_fbc(
        contract=client_contract,
        method_name='doInfinite',
        target_block=web3.eth.blockNumber + 10,
        payment=12345,
        donation=54321,
    )

    chain.wait.for_block(fbc.call().targetBlock())

    execute_txn_hash = fbc.transact().execute()
    execute_txn_receipt = chain.wait.for_receipt(execute_txn_hash)
    execute_txn = web3.eth.getTransaction(execute_txn_hash)

    execute_filter = CallLib.pastEvents('CallExecuted', {'address': fbc.address})
    execute_logs = execute_filter.get()
    assert len(execute_logs) == 1
    execute_log_data = execute_logs[0]

    assert execute_log_data['args']['success'] is False

    gas_used = execute_txn_receipt['gasUsed']
    gas_price = execute_txn['gasPrice']
    expected_gas_cost = gas_used * gas_price
    recorded_gas_cost = execute_log_data['args']['gasCost']

    assert expected_gas_cost <= recorded_gas_cost
    assert abs(expected_gas_cost - recorded_gas_cost) < 1000
