def test_cannot_execute_if_claimed_by_other(deploy_client, deployed_contracts,
                                            deploy_coinbase,
                                            deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    target_block = deploy_client.get_block_number() + 300

    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=target_block,
    )

    deploy_client.wait_for_block(target_block - 10 - 255)

    # claim it
    claim_txn_h = call.claim(value=2 * call.basePayment())
    claim_txn_r = deploy_client.wait_for_transaction(claim_txn_h)

    assert call.claimer() == deploy_coinbase

    deploy_client.wait_for_block(call.targetBlock())

    assert call.wasCalled() is False

    not_allowed_txn_h = call.execute(_from=encode_hex(accounts[1]))
    not_allowed_txn_r = deploy_client.wait_for_transaction(not_allowed_txn_h)

    assert call.wasCalled() is False

    deploy_client.wait_for_block(call.targetBlock() + 64)

    ffa_txn_h = call.execute(_from=encode_hex(accounts[1]))
    ffa_txn_r = deploy_client.wait_for_transaction(ffa_txn_h)

    assert call.wasCalled() is True
