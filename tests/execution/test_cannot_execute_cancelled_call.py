import pytest

from ethereum import abi
from ethereum import utils
from ethereum.tester import TransactionFailed


deploy_contracts = [
    "CallLib",
    "TestCallExecution",
]


def test_execution_of_call_with_single_bool(deploy_client, deployed_contracts,
                                            deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(client_contract.setBool)

    # cancel it
    cancel_txn_h = call.cancel()
    cancel_txn_r = deploy_client.wait_for_transaction(cancel_txn_h)

    deploy_client.wait_for_block(call.targetBlock())

    with pytest.raises(TransactionFailed):
        call.execute()
