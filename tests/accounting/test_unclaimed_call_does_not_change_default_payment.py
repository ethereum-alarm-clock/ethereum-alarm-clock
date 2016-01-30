
deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestCallExecution",
]


def test_unclaimed_call_does_not_change_default_payment(deploy_client,
                                                        deployed_contracts,
                                                        deploy_future_block_call,
                                                        denoms,
                                                        FutureBlockCall,
                                                        CallLib, SchedulerLib,
                                                        get_call,
                                                        get_execution_data,
                                                        deploy_coinbase):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    scheduling_txn_hash = scheduler.scheduleCall(
        client_contract._meta.address,
        client_contract.noop.encoded_abi_signature,
        value=10 * denoms.ether,
        gas=3000000,
    )
    scheduling_txn = deploy_client.get_transaction_by_hash(scheduling_txn_hash)

    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn_hash)
    call = get_call(scheduling_txn_hash)

    deploy_client.wait_for_block(call.targetBlock())

    default_payment_before = scheduler.defaultPayment()

    execute_txn_hash = call.execute()
    execute_txn_receipt = deploy_client.wait_for_transaction(execute_txn_hash)

    assert call.wasCalled()
    assert scheduler.defaultPayment() == default_payment_before
