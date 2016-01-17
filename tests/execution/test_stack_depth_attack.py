import pytest

from ethereum import abi
from ethereum import utils
from ethereum.tester import TransactionFailed


deploy_contracts = [
    "Scheduler",
    "TestErrors",
]

MAX_CALL_DEPTH = 339
MAX_PRE_DRILL = 336


def test_stack_depth_does_not_call_if_cannot_reach_depth(deploy_client,
                                                         deployed_contracts,
                                                         deploy_future_block_call):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestErrors
    client_contract.reset()

    call = deploy_future_block_call(
        client_contract.doStackExtension,
        call_data=client_contract.doStackExtension.abi_args_signature([340]),
        require_depth=1000,
    )
    assert call.requiredStackDepth() == 1000

    client_contract.setCallAddress(call._meta.address)

    deploy_client.wait_for_block(call.targetBlock())

    assert client_contract.value() is False

    # Call such that the stack has been "significantly" extended prior to
    # executing the call.
    bad_call_txn_hash = client_contract.proxyCall(1000)
    bad_call_txn_receipt = deploy_client.wait_for_transaction(bad_call_txn_hash)

    assert call.wasCalled() is False
    assert client_contract.value() is False

    logs = deployed_contracts.CallLib._CallAborted.get_transaction_logs(bad_call_txn_hash)
    assert logs
    log_data = deployed_contracts.CallLib._CallAborted.get_log_data(logs[0])
    assert log_data['reason'].startswith('STACK_TOO_DEEP')

    call_txn_hash = client_contract.proxyCall(0)
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    assert call.wasCalled() is True
    assert client_contract.value() is True
