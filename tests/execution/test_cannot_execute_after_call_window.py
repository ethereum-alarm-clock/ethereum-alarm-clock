def test_cannot_execute_after_call_window(deploy_client, deployed_contracts,
                                          deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(client_contract.setBool)

    deploy_client.wait_for_block(call.targetBlock() + call.gracePeriod() + 1)

    assert call.wasCalled() is False

    txn_h = call.execute()
    txn_r = deploy_client.wait_for_transaction(txn_h)

    assert call.wasCalled() is False
