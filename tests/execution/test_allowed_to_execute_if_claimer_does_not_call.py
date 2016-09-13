def test_cannot_execute_if_claimed_by_other(chain, web3, deploy_fbc):
    client_contract = chain.get_contract('TestCallExecution')

    target_block = web3.eth.blockNumber + 300

    fbc = deploy_fbc(
        client_contract,
        method_name='setBool',
        target_block=target_block,
    )

    chain.wait.for_block(target_block - 10 - 255)

    # claim it
    claim_txn_h = fbc.transact({'value': 2 * fbc.call().basePayment()}).claim()
    chain.wait.for_receipt(claim_txn_h)

    assert fbc.call().claimer() == web3.eth.coinbase

    chain.wait.for_block(target_block)

    assert fbc.call().wasCalled() is False

    not_allowed_txn_h = fbc.transact({'from': web3.eth.accounts[1]}).execute()
    chain.wait.for_receipt(not_allowed_txn_h)

    assert fbc.call().wasCalled() is False

    chain.wait.for_block(target_block + 64)

    ffa_txn_h = fbc.transact({'from': web3.eth.accounts[1]}).execute()
    chain.wait.for_receipt(ffa_txn_h)

    assert fbc.call().wasCalled() is True
