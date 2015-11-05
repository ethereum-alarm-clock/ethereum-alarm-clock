deploy_contracts = [
    "CallLib",
    "TestCallExecution",
]


def test_cancelling_a_call_before_call_window(deploy_client,
                                              deployed_contracts,
                                              deploy_future_block_call,
                                              CallLib):
    client_contract = deployed_contracts.TestCallExecution

    target_block = deploy_client.get_block_number() + 20
    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=target_block,
    )
    deploy_client.wait_for_block(target_block - 11)

    assert len(deploy_client.get_code(call._meta.address)) > 3

    cancel_txn_hash = call.cancel()
    deploy_client.wait_for_transaction(cancel_txn_hash)

    cancel_logs = CallLib.Cancelled.get_transaction_logs(cancel_txn_hash)
    assert len(cancel_logs) == 1

    assert len(deploy_client.get_code(call._meta.address)) < 3


def test_cancelling_a_call_after_call_window(deploy_client,
                                             deployed_contracts,
                                             deploy_future_block_call,
                                             CallLib):
    client_contract = deployed_contracts.TestCallExecution

    target_block = deploy_client.get_block_number() + 20
    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=target_block,
    )
    deploy_client.wait_for_block(target_block + 256)

    assert len(deploy_client.get_code(call._meta.address)) > 3

    cancel_txn_hash = call.cancel()
    deploy_client.wait_for_transaction(cancel_txn_hash)

    cancel_logs = CallLib.Cancelled.get_transaction_logs(cancel_txn_hash)
    assert len(cancel_logs) == 1

    assert len(deploy_client.get_code(call._meta.address)) < 3
