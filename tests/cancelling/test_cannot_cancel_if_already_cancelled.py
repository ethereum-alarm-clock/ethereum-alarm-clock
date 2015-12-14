import pytest

from ethereum.tester import TransactionFailed


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

    assert call.is_cancelled() is False

    cancel_txn_h = call.cancel()
    cancel_txn_r = deploy_client.wait_for_transaction(cancel_txn_h)

    assert call.is_cancelled() is True

    with pytest.raises(TransactionFailed):
        call.cancel()
