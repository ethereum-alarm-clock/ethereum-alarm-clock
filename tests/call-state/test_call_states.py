
import pytest

from ethereum import abi
from ethereum import utils


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



def test_call_cancellation_states_before_call_window(deploy_client, deployed_contracts,
                                                     deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=deploy_client.get_block_number() + 400,
    )

    assert call.state() == State.Pending

    cancel_txn_hash = call.cancel()
    cancel_txn_receipt = deploy_client.wait_for_transaction(cancel_txn_hash)

    assert call.state() == State.Cancelled


def test_states_when_claimed(deploy_client, deployed_contracts,
                             deploy_future_block_call, denoms):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=deploy_client.get_block_number() + 400,
    )

    assert call.state() == State.Pending

    deploy_client.wait_for_block(call.targetBlock() - 10 - 100)

    assert call.state() == State.Unclaimed

    claim_txn_hash = call.claim(value=2 * denoms.ether)
    claim_txn_receipt = deploy_client.wait_for_transaction(claim_txn_hash)

    assert call.state() == State.Claimed

    deploy_client.wait_for_block(call.targetBlock() - 9)

    assert call.state() == State.Frozen

    deploy_client.wait_for_block(call.targetBlock())

    assert call.state() == State.Callable

    execute_txn_hash = call.execute()
    execute_txn_receipt = deploy_client.wait_for_transaction(execute_txn_hash)

    assert call.state() == State.Executed


def test_states_when_unclaimed(deploy_client, deployed_contracts,
                               deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=deploy_client.get_block_number() + 400,
    )

    assert call.state() == State.Pending

    deploy_client.wait_for_block(call.targetBlock() - 9)

    assert call.state() == State.Frozen

    deploy_client.wait_for_block(call.targetBlock())

    assert call.state() == State.Callable

    execute_txn_hash = call.execute()
    execute_txn_receipt = deploy_client.wait_for_transaction(execute_txn_hash)

    assert call.state() == State.Executed


def test_missed_state_when_claimed(deploy_client, deployed_contracts,
                                   deploy_future_block_call, denoms):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=deploy_client.get_block_number() + 400,
    )

    assert call.state() == State.Pending

    deploy_client.wait_for_block(call.targetBlock() - 10 - 100)

    assert call.state() == State.Unclaimed

    claim_txn_hash = call.claim(value=2 * denoms.ether)
    claim_txn_receipt = deploy_client.wait_for_transaction(claim_txn_hash)

    assert call.state() == State.Claimed

    deploy_client.wait_for_block(call.targetBlock())

    assert call.state() == State.Callable

    deploy_client.wait_for_block(call.targetBlock() + call.gracePeriod())

    assert call.state() == State.Missed


def test_missed_state_when_not_claimed(deploy_client, deployed_contracts,
                                       deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setBool,
        target_block=deploy_client.get_block_number() + 400,
    )

    assert call.state() == State.Pending

    deploy_client.wait_for_block(call.targetBlock() - 10 - 100)

    assert call.state() == State.Unclaimed

    deploy_client.wait_for_block(call.targetBlock())

    assert call.state() == State.Callable

    deploy_client.wait_for_block(call.targetBlock() + call.gracePeriod())

    assert call.state() == State.Missed
