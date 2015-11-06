deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestCallExecution",
    "TestDataRegistry",
]


def test_basic_call_scheduling(deploy_client, deployed_contracts,
                               deploy_future_block_call, denoms,
                               FutureBlockCall, CallLib, SchedulerLib,
                               get_call, get_execution_data):
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

    call = get_call(scheduling_txn)

    deploy_client.wait_for_block(call.targetBlock())

    assert client_contract.v_bool() is False

    call_txn_hash = scheduler.execute(call._meta.address)
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    execution_data = get_execution_data(call_txn_hash)

    assert execution_data['success'] is True
    assert client_contract.v_bool() is True
