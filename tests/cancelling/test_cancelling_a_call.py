deploy_contracts = [
    "CallLib",
    "TestCallExecution",
]


def test_cancelling_a_call_before_bid_window(deploy_client, deployed_contracts,
                                             deploy_future_block_call,
                                             CallLib):
    client_contract = deployed_contracts.TestCallExecution

    target_block = deploy_client.get_block_number() + 300
    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=target_block,
    )
    first_bid_block = target_block - 240 - 15 - 10
    deploy_client.wait_for_block(first_bid_block - 2)

    assert call.is_cancelled() is False

    cancel_txn_h = call.cancel()
    cancel_txn_r = deploy_client.wait_for_transaction(cancel_txn_h)

    assert int(cancel_txn_r['blockNumber'], 16) == first_bid_block - 1

    assert call.is_cancelled() is True

    cancel_logs = CallLib.Cancelled.get_transaction_logs(cancel_txn_h)
    assert len(cancel_logs) == 1


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

    assert call.is_cancelled() is False

    cancel_txn_hash = call.cancel()
    deploy_client.wait_for_transaction(cancel_txn_hash)

    cancel_logs = CallLib.Cancelled.get_transaction_logs(cancel_txn_hash)
    assert len(cancel_logs) == 1

    assert call.is_cancelled() is True
