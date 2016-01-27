
import pytest

from ethereum import abi
from ethereum import utils
from ethereum.tester import accounts


deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestCallExecution",
]


class State(object):
    Pending = 0
    Unclaimed = 1
    Claimed = 2
    Frozen = 3
    Callable = 4
    Executed = 5
    Cancelled = 6
    Missed = 7



def test_is_cancellable_before_call_window(deploy_client, deployed_contracts,
                                           deploy_coinbase, deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        scheduler_address=deploy_coinbase,
        target_block=deploy_client.get_block_number() + 400,
    )

    assert call.isCancellable() is True

    # false for non-scheduler account
    assert call.isCancellable(_from=utils.encode_hex(accounts[1])) is False

    cancel_txn_hash = call.cancel()
    cancel_txn_receipt = deploy_client.wait_for_transaction(cancel_txn_hash)

    assert call.isCancellable() is False


def test_not_cancellable_during_claim_window_and_call_window(deploy_client,
                                                             deployed_contracts,
                                                             deploy_future_block_call,
                                                             deploy_coinbase,
                                                             denoms):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        scheduler_address=deploy_coinbase,
        target_block=deploy_client.get_block_number() + 400,
    )

    assert call.state() == State.Pending
    assert call.isCancellable() is True

    # false for non-scheduler account
    assert call.isCancellable(_from=utils.encode_hex(accounts[1])) is False

    deploy_client.wait_for_block(call.firstClaimBlock())

    assert call.isCancellable() is False

    claim_txn_hash = call.claim(value=2 * denoms.ether)
    claim_txn_receipt = deploy_client.wait_for_transaction(claim_txn_hash)

    assert call.state() == State.Claimed
    assert call.isCancellable() is False

    deploy_client.wait_for_block(call.targetBlock() - 9)

    assert call.state() == State.Frozen
    assert call.isCancellable() is False

    deploy_client.wait_for_block(call.targetBlock())

    assert call.state() == State.Callable
    assert call.isCancellable() is False

    execute_txn_hash = call.execute()
    execute_txn_receipt = deploy_client.wait_for_transaction(execute_txn_hash)

    assert call.state() == State.Executed
    assert call.isCancellable() is False


def test_cancellable_after_call_window_if_missed(deploy_client,
                                                 deployed_contracts,
                                                 deploy_future_block_call,
                                                 deploy_coinbase,
                                                 denoms):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        scheduler_address=deploy_coinbase,
        target_block=deploy_client.get_block_number() + 400,
    )

    assert call.state() == State.Pending

    deploy_client.wait_for_block(call.targetBlock() + call.gracePeriod())

    assert call.state() == State.Missed

    assert call.isCancellable() is True
    # true for non-scheduler account
    assert call.isCancellable(_from=utils.encode_hex(accounts[1])) is True

    cancel_txn_hash = call.cancel()
    cancel_txn_receipt = deploy_client.wait_for_transaction(cancel_txn_hash)

    assert call.isCancellable() is False
    assert call.isCancellable(_from=utils.encode_hex(accounts[1])) is False
