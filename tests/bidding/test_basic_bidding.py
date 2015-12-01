deploy_contracts = [
    "CallLib",
    "Scheduler",
    "AccountingLib",
    "TestCallExecution",
    "TestDataRegistry",
]


def test_basic_call_scheduling(deploy_client, deployed_contracts,
                               deploy_future_block_call, denoms,
                               FutureBlockCall, CallLib, SchedulerLib,
                               get_call, get_execution_data):
    client_contract = deployed_contracts.TestCallExecution
    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=deploy_client.get_block_number() + 1000,
        payment=denoms.ether,
    )

    assert call.checkBid() == 0

    import ipdb; ipdb.set_trace()
    bid_txn_h = call.bid(denoms.ether, value=2*denoms.ether)
    bid_txn_r = deploy_client.wait_for_transaction(bid_txn_h)

    deploy_client.wait_for_block(call.targetBlock())

    assert call.checkBid() == denoms.ether
