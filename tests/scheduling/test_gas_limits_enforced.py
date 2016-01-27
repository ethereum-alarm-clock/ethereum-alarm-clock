
deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestCallExecution",
]


def test_call_rejected_for_too_low_gas_requirement(deploy_client,
                                                   deployed_contracts,
                                                   deploy_future_block_call,
                                                   denoms, FutureBlockCall,
                                                   CallLib, SchedulerLib,
                                                   get_call_rejection_data,
                                                   deploy_coinbase):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    targetBlock = scheduler.getFirstSchedulableBlock() + 10

    # 1 wei short
    assert 100 < scheduler.getMinimumCallGas()

    scheduling_txn_hash = scheduler.scheduleCall(
        client_contract._meta.address,
        client_contract.setBool.encoded_abi_signature,
        targetBlock,
        100,
        value=10 * denoms.ether,
    )
    scheduling_txn = deploy_client.get_transaction_by_hash(scheduling_txn_hash)

    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn_hash)

    rejection_data = get_call_rejection_data(scheduling_txn_hash)
    assert rejection_data['reason'] == 'REQUIRED_GAS_TOO_LOW'


def test_call_rejected_for_too_high_gas_requirement(deploy_client,
                                                    deployed_contracts,
                                                    deploy_future_block_call,
                                                    denoms, FutureBlockCall,
                                                    CallLib, SchedulerLib,
                                                    get_call_rejection_data,
                                                    deploy_coinbase):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    targetBlock = scheduler.getFirstSchedulableBlock() + 10

    # 1 wei short
    assert 100 < scheduler.getMinimumCallGas()

    scheduling_txn_hash = scheduler.scheduleCall(
        client_contract._meta.address,
        client_contract.setBool.encoded_abi_signature,
        targetBlock,
        3141592,
        value=10 * denoms.ether,
    )
    scheduling_txn = deploy_client.get_transaction_by_hash(scheduling_txn_hash)

    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn_hash)

    rejection_data = get_call_rejection_data(scheduling_txn_hash)
    assert rejection_data['reason'] == 'REQUIRED_GAS_TOO_HIGH'
