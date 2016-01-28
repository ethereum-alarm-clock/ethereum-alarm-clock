import pytest

from ethereum import abi
from ethereum import utils


deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestCallExecution",
]


def test_sending_ether_with_execution(deploy_client, deployed_contracts,
                                      deploy_future_block_call, get_call,
                                      denoms):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(client_contract.setBool, call_value=5 * denoms.ether)
    deploy_client.wait_for_block(call.targetBlock())

    assert client_contract.get_balance() == 0

    call_txn_hash = call.execute()
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.get_balance() == 5 * denoms.ether
