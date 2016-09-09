def test_claiming_during_growth_window(chain, web3, deploy_fbc, denoms):
    target_block = web3.eth.blockNumber + 300
    fbc = deploy_fbc(
        target_block=target_block,
        payment=1 * denoms.ether,
    )

    base_payment = fbc.call().basePayment()

    first_claim_block = target_block - 255 - 10

    claim_at_block = first_claim_block + 42

    chain.wait.for_block(claim_at_block - 1)

    assert fbc.call().claimer() == "0x0000000000000000000000000000000000000000"

    txn_h = fbc.transact({'value': 2 * base_payment}).claim()
    txn_r = chain.wait.for_receipt(txn_h)

    assert txn_r['blockNumber'] == claim_at_block

    assert fbc.call().claimer() == web3.eth.coinbase
    assert fbc.call().claimerDeposit() == 2 * base_payment
    assert fbc.call().claimAmount() == 42 * base_payment / 240
