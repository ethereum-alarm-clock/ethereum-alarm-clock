import pytest

from ethereum import abi
from ethereum import utils


deploy_contracts = [
    "CallLib",
    "TestCallExecution",
]


def test_stack_(deploy_client, deployed_contracts,
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(client_contract.setBool)
    deploy_client.wait_for_block(call.targetBlock())

    assert client_contract.v_bool() is False

    call_txn_hash = call.execute()
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.v_bool() is True
