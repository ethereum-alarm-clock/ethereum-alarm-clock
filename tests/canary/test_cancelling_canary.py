deploy_contracts = [
    "Scheduler",
]


def test_canary_cancellation(canary, deploy_client, denoms, deployed_contracts,
                             FutureBlockCall):
    scheduler = deployed_contracts.Scheduler

    init_txn_h = canary.initialize()
    init_txn_r = deploy_client.wait_for_transaction(init_txn_h)

    call_contract_address = canary.callContractAddress()

    # check that the call was scheduled
    assert call_contract_address != "0x0000000000000000000000000000000000000000"
    assert scheduler.isKnownCall(call_contract_address) is True

    # check that the heartbeat went up
    assert canary.heartbeatCount() == 0

    call_contract = FutureBlockCall(call_contract_address, deploy_client)

    # check that it has enough funds to successfully heartbeat
    assert canary.get_balance() > 0
    assert call_contract.isCancelled() is False

    cancel_txn_h = canary.cancel()
    cancel_txn_r = deploy_client.wait_for_transaction(cancel_txn_h)

    assert canary.get_balance() == 0
    assert call_contract.isCancelled() is True
