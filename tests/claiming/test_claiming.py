deploy_contracts = [
    "CallLib",
    "Scheduler",
    "AccountingLib",
    "TestCallExecution",
    "TestDataRegistry",
]


def test_claiming(deploy_client, deployed_contracts, deploy_future_block_call,
                  denoms, FutureBlockCall, CallLib, SchedulerLib, get_call,
                  get_execution_data):
    client_contract = deployed_contracts.TestCallExecution
    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=deploy_client.get_block_number() + 1000,
        payment=denoms.ether,
    )

    target_block = call.target_block()
    base_payment = call.base_payment()

    first_claim_block = target_block - 255 - 10
    peak_claim_block = target_block - 10 - 15
    last_claim_block = target_block - 10

    assert call.get_bid_amount_for_block(first_claim_block) == 0

    for i in range(240):
        assert call.get_bid_amount_for_block(first_claim_block + i) == base_payment * i / 240

    assert call.get_bid_amount_for_block(peak_claim_block) == call.base_payment()

    for i in range(15):
        assert call.get_bid_amount_for_block(peak_claim_block + i) == call.base_payment()

    assert call.get_bid_amount_for_block(last_claim_block) == call.base_payment()

    assert deploy_client.get_block_number() < first_claim_block - 1
    deploy_client.wait_for_block(first_claim_block - 1)

    claim_txn_h = call.claim(value=2 * base_payment)
    claim_txn_r = deploy_client.wait_for_transaction(claim_txn_h)

    # TODO: see that bid is set correctly and that coinbase is bidder.
    assert call.checkBid() == denoms.ether

    update_claim_txn_h = call.claim(750 * denoms.finney)
    update_claim_txn_r = deploy_client.wait_for_transaction(update_claim_txn_h)

    assert call.checkBid() == 750 * denoms.finney
