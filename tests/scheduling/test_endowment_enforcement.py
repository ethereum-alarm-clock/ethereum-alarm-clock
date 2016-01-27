deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestCallExecution",
]


def test_call_rejected_for_insufficient_endowment(deploy_client,
                                                  deployed_contracts,
                                                  deploy_future_block_call,
                                                  denoms, FutureBlockCall,
                                                  CallLib, SchedulerLib,
                                                  get_call_rejection_data,
                                                  deploy_coinbase):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    targetBlock = scheduler.getFirstSchedulableBlock() + 1

    # 1 wei short
    endowment = 5 * denoms.ether + 2 * (scheduler.getDefaultPayment() + scheduler.getDefaultDonation()) + scheduler.getDefaultRequiredGas() * deploy_client.get_gas_price() - 1

    scheduling_txn_hash = scheduler.scheduleCall(
        client_contract._meta.address,
        5 * denoms.ether,
        client_contract.setBool.encoded_abi_signature,
        value=endowment,
    )
    scheduling_txn = deploy_client.get_transaction_by_hash(scheduling_txn_hash)

    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn_hash)

    rejection_data = get_call_rejection_data(scheduling_txn_hash)
    assert rejection_data['reason'] == 'INSUFFICIENT_FUNDS'


def test_call_accepted_for_sufficient_endowment(deploy_client,
                                                deployed_contracts,
                                                deploy_future_block_call,
                                                denoms, FutureBlockCall,
                                                CallLib, SchedulerLib,
                                                get_call, deploy_coinbase):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    targetBlock = scheduler.getFirstSchedulableBlock() + 1

    # 1 wei short
    endowment = 5 * denoms.ether + 2 * (scheduler.getDefaultPayment() + scheduler.getDefaultDonation()) + scheduler.getDefaultRequiredGas() * deploy_client.get_gas_price() - 1

    scheduling_txn_hash = scheduler.scheduleCall(
        client_contract._meta.address,
        5 * denoms.ether,
        client_contract.setBool.encoded_abi_signature,
        value=endowment,
    )
    scheduling_txn = deploy_client.get_transaction_by_hash(scheduling_txn_hash)

    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn_hash)

    call = get_call(scheduling_txn_hash)
    assert call.callValue() == 5 * denoms.ether
    assert call.basePayment() == scheduler.getDefaultPayment()
    assert call.baseDonation() == scheduler.getDefaultDonation()
    assert call.requiredGas == scheduler.getDefaultRequiredGas()
