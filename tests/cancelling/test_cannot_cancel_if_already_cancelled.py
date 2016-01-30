deploy_contracts = [
    "CallLib",
    "TestCallExecution",
]


def test_cannot_cancel_if_already_cancelled(deploy_client, deployed_contracts,
                                            deploy_future_block_call, CallLib):
    client_contract = deployed_contracts.TestCallExecution

    target_block = deploy_client.get_block_number() + 300
    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=target_block,
    )

    assert call.isCancelled() is False

    cancel_txn_h = call.cancel()
    cancel_txn_r = deploy_client.wait_for_transaction(cancel_txn_h)
    assert len(CallLib.Cancelled.get_transaction_logs(cancel_txn_h)) == 1

    assert call.isCancelled() is True

    duplicate_cancel_txn_h = call.cancel()
    duplicate_cancel_txn_receipt = deploy_client.wait_for_transaction(duplicate_cancel_txn_h)
    assert len(CallLib.Cancelled.get_transaction_logs(duplicate_cancel_txn_h)) == 0
