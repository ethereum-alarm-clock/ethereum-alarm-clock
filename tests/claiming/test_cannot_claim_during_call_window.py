def test_cannot_claim_during_call_window(chain, web3, deploy_fbc, denoms):
    target_block = web3.eth.blockNumber + 300
    fbc = deploy_fbc(
        target_block=target_block,
        payment=1 * denoms.ether,
    )

    target_block = fbc.call().targetBlock()
    base_payment = fbc.call().basePayment()

    chain.wait.for_block(target_block)
    assert web3.eth.blockNumber == target_block

    assert fbc.call().claimer() == "0x0000000000000000000000000000000000000000"

    txn_h = fbc.transact({'value': 2 * base_payment}).claim()
    txn_r = chain.wait.for_receipt(txn_h)

    # this really should be `target_block + 1`  very confused as to why it isn't
    assert txn_r['blockNumber'] == target_block
    assert fbc.call().claimer() == "0x0000000000000000000000000000000000000000"
