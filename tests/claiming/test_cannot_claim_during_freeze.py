def test_cannot_claim_during_freeze_window(chain, web3, deploy_fbc, denoms,
                                           CallStates):
    target_block = web3.eth.blockNumber + 300,
    fbc = deploy_fbc(
        target_block=target_block,
        payment=1 * denoms.ether,
    )

    target_block = fbc.call().targetBlock()
    base_payment = fbc.call().basePayment()

    chain.wait.for_block(target_block - 10)
    assert fbc.call().state() == CallStates.Frozen

    assert fbc.call().claimer() == "0x0000000000000000000000000000000000000000"

    txn_h = fbc.transact({'value': 2 * base_payment}).claim()
    txn_r = chain.wait.for_receipt(txn_h)

    assert txn_r['target_block'] == target_block - 9
    assert fbc.call().claimer() == "0x0000000000000000000000000000000000000000"
