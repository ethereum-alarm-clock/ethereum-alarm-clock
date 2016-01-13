deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestCallExecution",
]


def test_gas_accounting_for_successful_call(deploy_client, deployed_contracts,
                                            deploy_future_block_call, denoms,
                                            FutureBlockCall, CallLib, SchedulerLib):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=deploy_client.get_block_number() + 1000,
        payment=12345,
        donation=54321,
    )

    deploy_client.wait_for_block(call.targetBlock())

    call_txn_hash = call.execute()
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)
    call_txn = deploy_client.get_transaction_by_hash(call_txn_hash)

    execute_logs = CallLib.CallExecuted.get_transaction_logs(call_txn_hash)
    assert len(execute_logs) == 1
    execute_data = CallLib.CallExecuted.get_log_data(execute_logs[0])

    assert execute_data['success'] is True

    gas_used = int(call_txn_receipt['gasUsed'], 16)
    gas_price = int(call_txn['gasPrice'], 16)
    actual_gas_cost = gas_used * gas_price
    expected_gas_cost = execute_data['gasCost']

    assert actual_gas_cost <= expected_gas_cost
    assert abs(actual_gas_cost - expected_gas_cost) < 1000
