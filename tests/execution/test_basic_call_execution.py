import pytest

from ethereum import abi
from ethereum import utils


deploy_contracts = [
    "CallLib",
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

    call = deploy_future_block_call(client_contract.setInt)
    deploy_client.wait_for_block(call.targetBlock())

    signature = call.registerData.encoded_abi_signature
    data = abi.encode_single(abi.process_type('int256'), -1234567890)
    txn_data = ''.join((utils.encode_hex(signature), utils.encode_hex(data)))

    data_txn_hash = deploy_client.send_transaction(
        to=call._meta.address,
        data=txn_data,
    )
    data_txn_receipt = deploy_client.wait_for_transaction(data_txn_hash)

    assert client_contract.v_int() == 0

    call_txn_hash = call.execute()
    deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.v_int() == -1234567890


def test_execution_of_call_with_single_uint(deploy_client, deployed_contracts,
                                            deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(client_contract.setUInt)
    deploy_client.wait_for_block(call.targetBlock())

    signature = call.registerData.encoded_abi_signature
    data = abi.encode_single(abi.process_type('uint256'), 1234567890)
    txn_data = ''.join((utils.encode_hex(signature), utils.encode_hex(data)))

    data_txn_hash = deploy_client.send_transaction(
        to=call._meta.address,
        data=txn_data,
    )
    data_txn_receipt = deploy_client.wait_for_transaction(data_txn_hash)

    assert client_contract.v_uint() == 0

    call_txn_hash = call.execute()
    deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.v_uint() == 1234567890


def test_execution_of_call_with_single_address(deploy_client,
                                               deployed_contracts,
                                               deploy_coinbase,
                                               deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(client_contract.setAddress)
    deploy_client.wait_for_block(call.targetBlock())

    signature = call.registerData.encoded_abi_signature
    data = abi.encode_single(abi.process_type('address'), deploy_coinbase[2:])
    txn_data = ''.join((utils.encode_hex(signature), utils.encode_hex(data)))

    data_txn_hash = deploy_client.send_transaction(
        to=call._meta.address,
        data=txn_data,
    )
    data_txn_receipt = deploy_client.wait_for_transaction(data_txn_hash)

    assert client_contract.v_address() == '0x0000000000000000000000000000000000000000'

    call_txn_hash = call.execute()
    deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.v_address() == deploy_coinbase


def test_execution_of_call_with_single_bytes32(deploy_client,
                                               deployed_contracts,
                                               deploy_coinbase,
                                               deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(client_contract.setBytes32)
    deploy_client.wait_for_block(call.targetBlock())

    value = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f'
    signature = call.registerData.encoded_abi_signature
    data = abi.encode_single(abi.process_type('bytes32'), value)
    txn_data = ''.join((utils.encode_hex(signature), utils.encode_hex(data)))

    data_txn_hash = deploy_client.send_transaction(
        to=call._meta.address,
        data=txn_data,
    )
    data_txn_receipt = deploy_client.wait_for_transaction(data_txn_hash)

    assert client_contract.v_bytes32() is None

    call_txn_hash = call.execute()
    deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.v_bytes32() == value


@pytest.mark.skipif(True, reason="bytes doesn't work")
def test_execution_of_call_with_single_bytes(deploy_client,
                                             deployed_contracts,
                                             deploy_coinbase,
                                             deploy_future_block_call,
                                             CallLib):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(client_contract.setBytes)
    deploy_client.wait_for_block(call.targetBlock())

    value = 'abcd'

    signature = call.registerData.encoded_abi_signature
    data = abi.encode_single(abi.process_type('bytes'), value)
    txn_data = ''.join((utils.encode_hex(signature), utils.encode_hex(data)))

    data_txn_hash = deploy_client.send_transaction(
        to=call._meta.address,
        data=txn_data,
    )
    data_txn_receipt = deploy_client.wait_for_transaction(data_txn_hash)

    assert client_contract.v_bytes() == ''
    assert call.callData() == data

    #call_txn_hash = call.execute()
    call_txn_hash = client_contract.setBytes(value)
    txn_r = deploy_client.wait_for_transaction(call_txn_hash)
    txn = deploy_client.get_transaction_by_hash(call_txn_hash)

    assert txn['input'] == txn_data

    call_logs = CallLib.CallExecuted.get_transaction_logs(call_txn_hash)
    call_data = [CallLib.CallExecuted.get_log_data(l) for l in call_logs]

    bytes_logs = client_contract.Bytes.get_transaction_logs(call_txn_hash)
    bytes_data = [client_contract.Bytes.get_log_data(l) for l in bytes_logs]

    assert client_contract.v_bytes() == value


@pytest.mark.skipif(True, reason="bytes doesn't work")
def test_execution_of_call_with_many_values(deploy_client,
                                            deployed_contracts,
                                            deploy_coinbase,
                                            deploy_future_block_call,
                                            CallLib):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(client_contract.setMany)
    deploy_client.wait_for_block(call.targetBlock())

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

    signature = call.registerData.encoded_abi_signature
    data = ''.join((
        abi.encode_single(abi.process_type(t), v)
        for t, v in zip(types, values)
    ))
    txn_data = ''.join((utils.encode_hex(signature), utils.encode_hex(data)))

    data_txn_hash = deploy_client.send_transaction(
        to=call._meta.address,
        data=txn_data,
    )
    data_txn_receipt = deploy_client.wait_for_transaction(data_txn_hash)


    assert client_contract.vm_a() == 0
    assert client_contract.vm_b() == 0
    assert client_contract.vm_c() == 0
    assert client_contract.vm_d() == None
    assert client_contract.vm_e() == '0x0000000000000000000000000000000000000000'
    assert client_contract.vm_f() == ''

    call_txn_hash = call.execute()
    txn_r = deploy_client.wait_for_transaction(call_txn_hash)

    call_logs = CallLib.CallExecuted.get_transaction_logs(call_txn_hash)
    call_data = [CallLib.CallExecuted.get_log_data(l) for l in call_logs]

    assert client_contract.vm_a() == values[0]
    assert client_contract.vm_b() == values[1]
    assert client_contract.vm_c() == values[2]
    assert client_contract.vm_d() == values[3]
    assert client_contract.vm_e() == '0xd3cda913deb6f67967b99d67acdfa1712c293601'
    assert client_contract.vm_f() == values[5]
