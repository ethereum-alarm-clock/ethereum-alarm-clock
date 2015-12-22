deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestCallExecution",
]


def test_execution_fee(deploy_client, deployed_contracts,
                       deploy_future_block_call, denoms,
                       FutureBlockCall, CallLib, SchedulerLib):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=deploy_client.get_block_number() + 1000,
        payment=12345,
        fee=54321,
    )

    deploy_client.wait_for_block(call.targetBlock())

    assert deploy_client.get_balance("0xd3cda913deb6f67967b99d67acdfa1712c293601") == 0

    assert client_contract.v_bool() is False
    assert client_contract.wasSuccessful() == 0

    call_txn_hash = client_contract.doExecution(call._meta.address)
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.wasSuccessful() == 1
    assert client_contract.v_bool() is True

    execute_logs = CallLib.CallExecuted.get_transaction_logs(call_txn_hash)
    assert len(execute_logs) == 1
    execute_data = CallLib.CallExecuted.get_log_data(execute_logs[0])

    assert execute_data['fee'] == 54321
    assert deploy_client.get_balance("0xd3cda913deb6f67967b99d67acdfa1712c293601") == 54321
