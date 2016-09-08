def test_cannot_claim_before_window(chain, web3, deploy_fbc, denoms):
    target_block = web3.eth.blockNumber + 300,
    fbc = deploy_fbc(
        target_block=target_block,
        payment=1 * denoms.ether,
    )

    target_block = fbc.call().targetBlock()
    base_payment = fbc.call().basePayment()

    first_claim_block = target_block - 255 - 10
    chain.wait.for_block(first_claim_block - 2)

    assert fbc.call().claimer() == "0x0000000000000000000000000000000000000000"

    txn_h = fbc.transact({'value': 2 * base_payment}).claim()
    txn_r = chain.wait.for_receipt(txn_h)

    assert txn_r['blockNumber'] == first_claim_block - 1

    assert fbc.call().claimer() == "0x0000000000000000000000000000000000000000"
