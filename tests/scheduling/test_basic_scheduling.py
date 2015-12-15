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

    target_block = deploy_client.get_block_number() + 300

    scheduling_txn = scheduler.schedule_call(
        client_contract._meta.address,
        client_contract.setBool.encoded_abi_signature,
        target_block,
        1000000,
        value=10 * denoms.ether,
        gas=3000000,
    )

    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn)
    call = get_call(scheduling_txn)

    assert call.target_block() == target_block
    assert call.grace_period() == 255
    assert call.suggested_gas() == 1000000
    assert call.base_payment() == denoms.ether
    assert call.base_fee() == denoms.ether
