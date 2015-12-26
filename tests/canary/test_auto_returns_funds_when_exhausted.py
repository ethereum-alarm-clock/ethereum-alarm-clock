deploy_contracts = [
    "Scheduler",
]


def test_canary_initialization(deploy_canary_contract, deploy_client, denoms,
                               deployed_contracts, FutureBlockCall):
    scheduler = deployed_contracts.Scheduler

    canary = deploy_canary_contract(endowment=int(4.005 * denoms.ether))

    prev_balance = canary.get_balance()

    init_txn_h = canary.heartbeat()
    init_txn_r = deploy_client.wait_for_transaction(init_txn_h)

    while canary.get_balance() < prev_balance:
        print prev_balance
        prev_balance = canary.get_balance()

        call_contract_address = canary.callContractAddress()
        assert scheduler.isKnownCall(call_contract_address) is True

        call_contract = FutureBlockCall(call_contract_address, deploy_client)
        deploy_client.wait_for_block(call_contract.targetBlock())

        exec_txn_h = call_contract.execute()
        exec_txn_r = deploy_client.wait_for_transaction(exec_txn_h)

        assert call_contract.wasCalled()

    assert canary.get_balance() == 0
