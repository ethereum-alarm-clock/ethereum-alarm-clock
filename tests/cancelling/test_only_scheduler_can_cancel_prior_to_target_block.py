import pytest

from ethereum.tester import (
    TransactionFailed,
    accounts,
    encode_hex,
)


deploy_contracts = [
    "CallLib",
    "TestCallExecution",
]


def test_only_scheduler_can_cancel_prior_to_target_block(deploy_client,
                                                         deployed_contracts,
                                                         deploy_future_block_call,
                                                         CallLib):
    client_contract = deployed_contracts.TestCallExecution

    target_block = deploy_client.get_block_number() + 300
    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=target_block,
    )

    assert call.isCancelled() is False

    with pytest.raises(TransactionFailed):
        call.cancel(_from=encode_hex(accounts[1]))
