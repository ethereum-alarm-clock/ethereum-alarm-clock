deploy_contracts = [
    "Scheduler",
]


def test_cannot_double_initialize(canary, deploy_client, denoms,
                                  deployed_contracts, FutureBlockCall):
    scheduler = deployed_contracts.Scheduler

    init_txn_h = canary.initialize()
    init_txn_r = deploy_client.wait_for_transaction(init_txn_h)

    call_contract_address = canary.callContractAddress()

    # sanity check
    assert call_contract_address != "0x0000000000000000000000000000000000000000"
    assert scheduler.isKnownCall(call_contract_address) is True

    bad_txn_h = canary.initialize()
    bad_txn_r = deploy_client.wait_for_transaction(init_txn_h)

    # check nothing changed
    assert canary.callContractAddress() == call_contract_address
