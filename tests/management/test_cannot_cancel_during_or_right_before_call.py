deploy_contracts = [
    "CallLib",
    "TestCallExecution",
]


def test_cannot_cancel_call_just_before_target_block(deploy_client,
                                                     deployed_contracts,
                                                     deploy_future_block_call,
                                                     CallLib):
    client_contract = deployed_contracts.TestCallExecution

    target_block = deploy_client.get_block_number() + 20
    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=target_block,
    )
    deploy_client.wait_for_block(target_block - 10)

    assert len(deploy_client.get_code(call._meta.address)) > 3

    cancel_txn_hash = call.cancel()
    deploy_client.wait_for_transaction(cancel_txn_hash)

    cancel_logs = CallLib.Cancelled.get_transaction_logs(cancel_txn_hash)
    assert not cancel_logs

    assert len(deploy_client.get_code(call._meta.address)) > 3
