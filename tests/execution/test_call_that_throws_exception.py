deploy_contracts = [
    "CallLib",
    "TestErrors",
]


def test_execution_of_call_that_throws_exception(deploy_client, deployed_contracts,
                                                 deploy_future_block_call):
    client_contract = deployed_contracts.TestErrors
    call = deploy_future_block_call(client_contract.doFail)

    assert client_contract.value() is False

    call_txn_hash = call.execute()
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)
    call_txn = deploy_client.get_transaction_by_hash(call_txn_hash)

    assert client_contract.value() is False

    call_logs = deployed_contracts.CallLib.CallExecuted.get_transaction_logs(call_txn_hash)
    assert len(call_logs) == 1
    log_data = deployed_contracts.CallLib.CallExecuted.get_log_data(call_logs[0])
    assert log_data['success'] is False

    gas_used = int(call_txn_receipt['gasUsed'], 16)
    gas_price = int(call_txn['gasPrice'], 16)

    assert gas_used * gas_price < log_data['gasCost']
