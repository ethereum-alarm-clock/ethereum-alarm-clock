deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestCallExecution",
    "TestDataRegistry",
]


def test_basic_call_scheduling(deploy_client, deployed_contracts,
                               deploy_future_block_call, denoms,
                               FutureBlockCall):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    scheduling_txn = scheduler.scheduleCall(
        client_contract._meta.address,
        client_contract.setBool.encoded_abi_signature,
        deploy_client.get_block_number() + 45,
        1000000,
        value=10 * denoms.ether,
        gas=3000000,
    )
    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn)

    call_scheduled_logs = deployed_contracts.SchedulerLib.CallScheduled.get_transaction_logs(scheduling_txn)
    assert len(call_scheduled_logs) == 1
    call_scheduled_data = deployed_contracts.SchedulerLib.CallScheduled.get_log_data(call_scheduled_logs[0])

    call_address = call_scheduled_data['callAddress']
    call = FutureBlockCall(call_address, deploy_client)

    deploy_client.wait_for_block(call.targetBlock())

    assert client_contract.v_bool() is False

    call_txn_hash = scheduler.execute(call_address)
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    execute_logs = deployed_contracts.CallLib.CallExecuted.get_transaction_logs(call_txn_hash)
    assert len(execute_logs) == 1
    execute_data = deployed_contracts.CallLib.CallExecuted.get_log_data(execute_logs[0])

    assert client_contract.v_bool() is True
