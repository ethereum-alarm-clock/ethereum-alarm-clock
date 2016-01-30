deploy_contracts = [
    "CallLib",
    "TestCallExecution",
]


def test_cannot_cancel_if_already_called(deploy_client, deployed_contracts,
                                         deploy_future_block_call, CallLib):
    client_contract = deployed_contracts.TestCallExecution

    target_block = deploy_client.get_block_number() + 300
    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=target_block,
    )

    deploy_client.wait_for_block(target_block)

    assert call.isCancelled() is False
    assert call.wasCalled() is False

    execute_txn_h = call.execute()
    execute_txn_r = deploy_client.wait_for_transaction(execute_txn_h)

    assert call.wasCalled() is True
    assert call.isCancelled() is False

    cancel_txn = call.cancel()
    cancel_txn_receipt = deploy_client.wait_for_transaction(cancel_txn)

    assert call.wasCalled() is True
    assert call.isCancelled() is False
