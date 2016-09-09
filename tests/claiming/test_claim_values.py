def test_claim_block_values(chain, web3, deploy_fbc, denoms):
    target_block = web3.eth.blockNumber + 300
    fbc = deploy_fbc(
        target_block=target_block,
        payment=1 * denoms.ether,
    )

    base_payment = fbc.call().basePayment()

    first_claim_block = target_block - 255 - 10
    peak_claim_block = target_block - 10 - 15
    last_claim_block = target_block - 10

    assert fbc.call().getClaimAmountForBlock(first_claim_block) == 0

    for i in range(240):
        assert fbc.call().getClaimAmountForBlock(first_claim_block + i) == base_payment * i / 240

    assert fbc.call().getClaimAmountForBlock(peak_claim_block) == base_payment

    for i in range(15):
        assert fbc.call().getClaimAmountForBlock(peak_claim_block + i) == base_payment

    assert fbc.call().getClaimAmountForBlock(last_claim_block) == base_payment
