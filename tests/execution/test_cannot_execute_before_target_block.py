import pytest

from ethereum import abi
from ethereum import utils
from ethereum.tester import TransactionFailed


deploy_contracts = [
    "CallLib",
    "TestCallExecution",
]


def test_cannot_execute_before_target_block(deploy_client, deployed_contracts,
                                            deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=deploy_client.get_block_number() + 20,
    )

    assert deploy_client.get_block_number() < call.targetBlock()
    deploy_client.wait_for_block(call.targetBlock() - 4)

    assert deploy_client.get_block_number() == call.targetBlock() - 4
    assert call.wasCalled() is False
    assert deploy_client.get_block_number() == call.targetBlock() - 2

    # at target - 1
    txn_h = call.execute()
    txn_r = deploy_client.wait_for_transaction(txn_h)

    assert call.wasCalled() is False
