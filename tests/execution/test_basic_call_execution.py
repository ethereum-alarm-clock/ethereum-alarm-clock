import pytest

from ethereum import abi
from ethereum import utils


deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestCallExecution",
]


def test_execution_of_call_with_single_bool(deploy_client, deployed_contracts,
                                            deploy_future_block_call, get_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(client_contract.setBool)
    deploy_client.wait_for_block(call.targetBlock())

    assert client_contract.v_bool() is False

    call_txn_hash = call.execute()
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.v_bool() is True


def test_execution_of_call_with_single_int(deploy_client, deployed_contracts,
                                           deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setInt,
        call_data=abi.encode_single(abi.process_type('int256'), -1234567890)
    )
    deploy_client.wait_for_block(call.targetBlock())

    assert client_contract.v_int() == 0

    call_txn_hash = call.execute()
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.v_int() == -1234567890


def test_execution_of_call_with_single_uint(deploy_client, deployed_contracts,
                                            deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setUInt,
        call_data=abi.encode_single(abi.process_type('uint256'), 1234567890),
    )
    deploy_client.wait_for_block(call.targetBlock())

    assert client_contract.v_uint() == 0

    call_txn_hash = call.execute()
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.v_uint() == 1234567890


def test_execution_of_call_with_single_address(deploy_client,
                                               deployed_contracts,
                                               deploy_coinbase,
                                               deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setAddress,
        call_data=abi.encode_single(abi.process_type('address'), deploy_coinbase[2:]),
    )
    deploy_client.wait_for_block(call.targetBlock())

    assert client_contract.v_address() == '0x0000000000000000000000000000000000000000'

    call_txn_hash = call.execute()
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.v_address() == deploy_coinbase


def test_execution_of_call_with_single_bytes32(deploy_client,
                                               deployed_contracts,
                                               deploy_coinbase,
                                               deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    value = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f'

    call = deploy_future_block_call(
        client_contract.setBytes32,
        call_data=abi.encode_single(abi.process_type('bytes32'), value),
    )
    deploy_client.wait_for_block(call.targetBlock())

    assert client_contract.v_bytes32() is None

    call_txn_hash = call.execute()
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.v_bytes32() == value


#@pytest.mark.skipif(True, reason="bytes doesn't work")
def test_execution_of_call_with_single_bytes(deploy_client,
                                             deployed_contracts,
                                             deploy_coinbase,
                                             deploy_future_block_call,
                                             CallLib):
    client_contract = deployed_contracts.TestCallExecution

    value = 'abcd'

    call = deploy_future_block_call(
        client_contract.setBytes,
        call_data=client_contract.setBytes.abi_args_signature([value]),
    )
    deploy_client.wait_for_block(call.targetBlock())


    assert client_contract.wasSuccessful() == 0
    assert client_contract.v_bytes() == ''

    call_txn_hash = call.execute()
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.wasSuccessful() == 1
    assert client_contract.v_bytes() == value


def test_execution_of_call_with_many_values(deploy_client,
                                            deployed_contracts,
                                            deploy_coinbase,
                                            deploy_future_block_call,
                                            CallLib):
    client_contract = deployed_contracts.TestCallExecution

    values = (
        1234567890,
        -1234567890,
        987654321,
        '\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13',
        'd3cda913deb6f67967b99d67acdfa1712c293601',
        'abcdefg',
    )
    types = (
        'uint256',
        'int256',
        'uint256',
        'bytes20',
        'address',
        'bytes',
    )


    call = deploy_future_block_call(
        client_contract.setMany,
        call_data=client_contract.setMany.abi_args_signature(values),
    )
    deploy_client.wait_for_block(call.targetBlock())

    assert client_contract.vm_a() == 0
    assert client_contract.vm_b() == 0
    assert client_contract.vm_c() == 0
    assert client_contract.vm_d() == None
    assert client_contract.vm_e() == '0x0000000000000000000000000000000000000000'
    assert client_contract.vm_f() == ''

    call_txn_hash = call.execute()
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.vm_a() == values[0]
    assert client_contract.vm_b() == values[1]
    assert client_contract.vm_c() == values[2]
    assert client_contract.vm_d() == values[3]
    assert client_contract.vm_e() == '0xd3cda913deb6f67967b99d67acdfa1712c293601'
    assert client_contract.vm_f() == values[5]
