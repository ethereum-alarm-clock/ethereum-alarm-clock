deploy_contracts = [
    "Scheduler",
]


def test_canary_initialization(canary, deploy_client, denoms,
                               deployed_contracts, FutureBlockCall):
    scheduler = deployed_contracts.Scheduler

    init_txn_h = canary.heartbeat()
    init_txn_r = deploy_client.wait_for_transaction(init_txn_h)

    call_contract_address = canary.callContractAddress()

    # check that the call was scheduled
    assert call_contract_address != "0x0000000000000000000000000000000000000000"
    assert scheduler.isKnownCall(call_contract_address) is True

    # check that the heartbeat went up
    assert canary.heartbeatCount() == 1

    # check that it has enough funds to successfully heartbeat
    assert canary.get_balance() >= 2 * denoms.ether

    call_contract = FutureBlockCall(call_contract_address, deploy_client)

    deploy_client.wait_for_block(call_contract.targetBlock())

    exec_txn_h = call_contract.execute()
    exec_txn_r = deploy_client.wait_for_transaction(exec_txn_h)

    assert call_contract.wasCalled()
    assert call_contract.wasSuccessful()

    next_call_contract_address = canary.callContractAddress()
    assert next_call_contract_address != call_contract_address
    assert scheduler.isKnownCall(next_call_contract_address)

    assert canary.heartbeatCount() == 2
