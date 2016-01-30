
deploy_contracts = [
    "Scheduler",
    "TestCallExecution",
]


def test_call_rejected_for_too_low_stack_depth_check(deploy_client,
                                                     deployed_contracts,
                                                     denoms,
                                                     get_call_rejection_data,):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    targetBlock = scheduler.getFirstSchedulableBlock() + 10

    assert 9 < scheduler.getMinimumStackCheck()

    scheduling_txn_hash = scheduler.scheduleCall(
        client_contract.setBool.encoded_abi_signature,
        '',
        9,
        255,
        0,
        targetBlock,
        1000000,
        1,
        1,
        value=10 * denoms.ether,
    )
    scheduling_txn = deploy_client.get_transaction_by_hash(scheduling_txn_hash)

    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn_hash)

    rejection_data = get_call_rejection_data(scheduling_txn_hash)
    assert rejection_data['reason'] == 'STACK_CHECK_OUT_OF_RANGE'


def test_call_rejected_for_too_high_gas_requirement(deploy_client,
                                                    deployed_contracts, denoms,
                                                    get_call_rejection_data,):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    targetBlock = scheduler.getFirstSchedulableBlock() + 10

    assert 1001 > scheduler.getMaximumStackCheck()

    scheduling_txn_hash = scheduler.scheduleCall(
        client_contract.setBool.encoded_abi_signature,
        '',
        9,
        255,
        0,
        targetBlock,
        1000000,
        1,
        1,
        value=10 * denoms.ether,
    )
    scheduling_txn = deploy_client.get_transaction_by_hash(scheduling_txn_hash)

    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn_hash)

    rejection_data = get_call_rejection_data(scheduling_txn_hash)
    assert rejection_data['reason'] == 'STACK_CHECK_OUT_OF_RANGE'
