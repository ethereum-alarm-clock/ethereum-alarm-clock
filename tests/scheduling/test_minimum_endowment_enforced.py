deploy_contracts = [
    "Scheduler",
    "TestCallExecution",
    "TestDataRegistry",
]


def test_minimum_endowment_enforced(deploy_client, deployed_contracts,
                                    deploy_future_block_call, denoms,
                                    FutureBlockCall, SchedulerLib, get_call):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    minimum_endowment = scheduler.getMinimumEndowment(denoms.ether, 100 * denoms.finney)
    now_block = deploy_client.get_block_number()

    bad_scheduling_txn = scheduler.scheduleCall(
        client_contract._meta.address,
        client_contract.setBool.encoded_abi_signature,
        now_block + 40 + 10 + 255,
        1000000,
        value=minimum_endowment - 1,
        gas=3000000,
    )
    bad_scheduling_receipt = deploy_client.wait_for_transaction(bad_scheduling_txn)

    call_rejected_logs = SchedulerLib.CallRejected.get_transaction_logs(bad_scheduling_txn)
    assert len(call_rejected_logs) == 1
    call_rejected_data = SchedulerLib.CallRejected.get_log_data(call_rejected_logs[0])

    assert call_rejected_data['reason'] == 'INSUFFICIENT_FUNDS'

    now_block = deploy_client.get_block_number()

    good_scheduling_txn = scheduler.scheduleCall(
        client_contract._meta.address,
        client_contract.setBool.encoded_abi_signature,
        now_block + 40 + 10 + 255,
        1000000,
        value=minimum_endowment,
        gas=3000000,
    )
    good_scheduling_receipt = deploy_client.wait_for_transaction(good_scheduling_txn)

    call = get_call(good_scheduling_txn)
