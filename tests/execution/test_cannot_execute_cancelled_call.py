def test_execution_of_call_with_single_bool(deploy_client, deployed_contracts,
                                            deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=deploy_client.get_block_number() + 400
    )

    # cancel it
    cancel_txn_h = call.cancel()
    cancel_txn_r = deploy_client.wait_for_transaction(cancel_txn_h)

    assert call.isCancelled() is True

    deploy_client.wait_for_block(call.targetBlock())

    assert call.targetBlock() < deploy_client.get_block_number() < call.targetBlock() + call.gracePeriod()
    assert call.wasCalled() is False

    execute_txn_h = call.execute()
    execute_txn_r = deploy_client.wait_for_transaction(execute_txn_h)

    assert call.wasCalled() is False
