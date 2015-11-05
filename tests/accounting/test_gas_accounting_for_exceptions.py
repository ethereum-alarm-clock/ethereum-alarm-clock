deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestErrors",
]


def test_gas_accounting_for_call_exception(deploy_client, deployed_contracts,
                                          deploy_future_block_call, denoms,
                                          FutureBlockCall, CallLib, SchedulerLib):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestErrors

    scheduling_txn = scheduler.scheduleCall(
        client_contract._meta.address,
        client_contract.doFail.encoded_abi_signature,
        deploy_client.get_block_number() + 45,
        1000000,
        value=10 * denoms.ether,
        gas=3000000,
    )
    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn)

    call_scheduled_logs = SchedulerLib.CallScheduled.get_transaction_logs(scheduling_txn)
    assert len(call_scheduled_logs) == 1
    call_scheduled_data = SchedulerLib.CallScheduled.get_log_data(call_scheduled_logs[0])

    call_address = call_scheduled_data['callAddress']
    call = FutureBlockCall(call_address, deploy_client)

    deploy_client.wait_for_block(call.targetBlock())

    call_txn_hash = scheduler.execute(call_address)
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)
    call_txn = deploy_client.get_transaction_by_hash(call_txn_hash)

    execute_logs = CallLib.CallExecuted.get_transaction_logs(call_txn_hash)
    assert len(execute_logs) == 1
    execute_data = CallLib.CallExecuted.get_log_data(execute_logs[0])

    assert execute_data['success'] is False

    gas_used = int(call_txn_receipt['gasUsed'], 16)
    gas_price = int(call_txn['gasPrice'], 16)
    actual_gas_cost = gas_used * gas_price
    expected_gas_cost = execute_data['gasCost']

    assert actual_gas_cost <= expected_gas_cost
    assert abs(actual_gas_cost - expected_gas_cost) < 1000
