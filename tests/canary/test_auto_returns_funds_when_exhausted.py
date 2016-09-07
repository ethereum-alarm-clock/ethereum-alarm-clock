deploy_contracts = [
    "Scheduler",
]


def test_canary_initialization(deploy_canary_contract, deploy_client, denoms,
                               deployed_contracts, FutureBlockCall):
    scheduler = deployed_contracts.Scheduler

    canary = deploy_canary_contract(endowment=int(4.003 * denoms.ether))

    prev_balance = canary.get_balance()

    assert canary.isAlive() is False

    init_txn_h = canary.initialize()
    init_txn_r = deploy_client.wait_for_transaction(init_txn_h)

    assert canary.isAlive() is True

    while canary.get_balance() < prev_balance:
        # uncomment to see how much heartbeats cost.
        print("Heartbeat Cost:", (canary.get_balance() - prev_balance) * 1.0 / denoms.ether)
        prev_balance = canary.get_balance()

        call_contract_address = canary.callContractAddress()
        assert scheduler.isKnownCall(call_contract_address) is True

        call_contract = FutureBlockCall(call_contract_address, deploy_client)
        deploy_client.wait_for_block(call_contract.targetBlock())

        exec_txn_h = call_contract.execute()
        exec_txn_r = deploy_client.wait_for_transaction(exec_txn_h)

        assert call_contract.wasCalled()

    assert canary.get_balance() == 0
