import pytest

from ethereum.tester import TransactionFailed


deploy_contracts = [
    "CallLib",
    "TestCallExecution",
]


def test_cancelling_a_call_during_bid_window(deploy_client, deployed_contracts,
                                             deploy_future_block_call,
                                             CallLib):
    client_contract = deployed_contracts.TestCallExecution

    target_block = deploy_client.get_block_number() + 300
    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=target_block,
    )
    first_bid_block = target_block - 240 - 15 - 10
    deploy_client.wait_for_block(first_bid_block - 1)

    assert call.is_cancelled() is False

    with pytest.raises(TransactionFailed):
        call.cancel()
