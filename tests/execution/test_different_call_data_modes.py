import pytest

from ethereum import abi
from ethereum import utils


deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestCallExecution",
]


def test_no_signature_or_calldata(deploy_client, deployed_contracts,
                                  deploy_future_block_call, get_call):
    client_contract = deployed_contracts.TestCallExecution
    client_contract.reset()

    call = deploy_future_block_call(scheduler_address=client_contract._meta.address)
    deploy_client.wait_for_block(call.targetBlock())

    assert client_contract.v_bytes() == ""

    call_txn_hash = call.execute()
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.v_bytes() == ""
    assert call.wasCalled() is True
    assert call.wasSuccessful() is True


def test_only_signature(deploy_client, deployed_contracts,
                        deploy_future_block_call, get_call):
    client_contract = deployed_contracts.TestCallExecution
    client_contract.reset()

    call = deploy_future_block_call(client_contract.setCallData)
    deploy_client.wait_for_block(call.targetBlock())

    assert client_contract.v_bytes() == ""

    call_txn_hash = call.execute()
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.v_bytes() == client_contract.setCallData.encoded_abi_signature


def test_only_call_data(deploy_client, deployed_contracts,
                        deploy_future_block_call, get_call):
    client_contract = deployed_contracts.TestCallExecution
    client_contract.reset()

    call_data = client_contract.setUInt.encoded_abi_signature + client_contract.setUInt.abi_args_signature([12345])

    call = deploy_future_block_call(
        scheduler_address=client_contract._meta.address,
        call_data=call_data,
    )
    deploy_client.wait_for_block(call.targetBlock())

    assert client_contract.v_uint() == 0

    call_txn_hash = call.execute()
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.v_uint() == 12345


def test_both_signature_and_call_data(deploy_client, deployed_contracts,
                                      deploy_future_block_call, get_call):
    client_contract = deployed_contracts.TestCallExecution
    client_contract.reset()

    sig = client_contract.setUInt.encoded_abi_signature
    call_data = client_contract.setUInt.abi_args_signature([12345])

    call = deploy_future_block_call(
        client_contract.setUInt,
        call_data=call_data,
    )
    deploy_client.wait_for_block(call.targetBlock())

    assert client_contract.v_uint() == 0

    call_txn_hash = call.execute()
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.v_uint() == 12345
