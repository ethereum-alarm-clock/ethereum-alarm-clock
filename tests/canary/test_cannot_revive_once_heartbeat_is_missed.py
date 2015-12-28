deploy_contracts = [
    "Scheduler",
]


def test_cannary_cannot_be_revived(canary, deploy_client, denoms,
                                   deployed_contracts, FutureBlockCall):
    scheduler = deployed_contracts.Scheduler

    init_txn_h = canary.initialize()
    init_txn_r = deploy_client.wait_for_transaction(init_txn_h)

    call_contract_address = canary.callContractAddress()

    # check that the call was scheduled
    assert call_contract_address != "0x0000000000000000000000000000000000000000"
    assert scheduler.isKnownCall(call_contract_address) is True

    # check that the heartbeat went up
    assert canary.heartbeatCount() == 0

    # check that it has enough funds to successfully heartbeat
    assert canary.get_balance() >= 2 * denoms.ether

    call_contract = FutureBlockCall(call_contract_address, deploy_client)

    # Wait till after the call
    deploy_client.wait_for_block(
        call_contract.targetBlock() + call_contract.gracePeriod() + 1
    )

    assert not canary.isAlive()

    revive_txn_h = canary.heartbeat()
    revive_txn_r = deploy_client.wait_for_transaction(revive_txn_h)

    # shouldn't be alive.  stats shouldn't have changed
    assert not canary.isAlive()
    assert canary.heartbeatCount() == 0
    assert canary.callContractAddress() == call_contract_address
