deploy_contracts = [
    "CallLib",
    "Scheduler",
    "AccountingLib",
    "TestCallExecution",
    "TestDataRegistry",
]


def test_cannot_claim_during_call_window(deploy_client, deployed_contracts,
                                         deploy_future_block_call, denoms,
                                         FutureBlockCall, CallLib, SchedulerLib,
                                         get_call, get_execution_data,
                                         deploy_coinbase):
    client_contract = deployed_contracts.TestCallExecution
    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=deploy_client.get_block_number() + 1000,
        payment=denoms.ether,
    )

    target_block = call.targetBlock()
    base_payment = call.basePayment()

    deploy_client.wait_for_block(target_block + 1)

    assert call.claimer() == "0x0000000000000000000000000000000000000000"

    txn_h = call.claim(value=2 * base_payment)
    txn_r = deploy_client.wait_for_transaction(txn_h)

    assert call.claimer() == "0x0000000000000000000000000000000000000000"
