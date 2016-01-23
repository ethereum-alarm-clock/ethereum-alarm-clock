import pytest

from ethereum import utils


deploy_contracts = [
    "CallLib",
    "TestDataRegistry",
    "TestCallExecution",
]


def test_int_data_registry_via_register_data(deploy_client, deployed_contracts,
                                             deploy_future_block_call, deploy_coinbase):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setInt,
        target_block=deploy_client.get_block_number() + 40,
    )

    value = -1234567890
    sig = call.registerData.encoded_abi_signature
    call_data = utils.encode_hex(sig + client_contract.setInt.abi_args_signature([value]))

    deploy_client.send_transaction(
        to=call._meta.address,
        data=call_data,
    )

    # FROM: abi.encode_single(abi.process_type('int256'), value)
    assert call.callData() == '\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xb6i\xfd.'


def test_uint_data_registry_via_register_data(deploy_client, deployed_contracts,
                                              deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setUInt,
        target_block=deploy_client.get_block_number() + 40,
    )

    value = 1234567890123456789012345678901234567890
    sig = call.registerData.encoded_abi_signature
    call_data = utils.encode_hex(sig + client_contract.setUInt.abi_args_signature([value]))

    deploy_client.send_transaction(
        to=call._meta.address,
        data=call_data,
    )

    # FROM: abi.encode_single(abi.process_type('uint256'), value)
    assert call.callData() == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xa0\xc9 u\xc0\xdb\xf3\xb8\xac\xbc_\x96\xce?\n\xd2'


def test_address_data_registry_via_register_data(deploy_client,
                                                 deployed_contracts,
                                                 deploy_coinbase,
                                                 deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setAddress,
        target_block=deploy_client.get_block_number() + 40,
    )

    value = '0xd3cda913deb6f67967b99d67acdfa1712c293601'
    sig = call.registerData.encoded_abi_signature
    call_data = utils.encode_hex(sig + client_contract.setAddress.abi_args_signature([value]))

    deploy_client.send_transaction(
        to=call._meta.address,
        data=call_data,
    )

    # FROM: abi.encode_single(abi.process_type('address'), 'd3cda913deb6f67967b99d67acdfa1712c293601')
    assert call.callData() == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd3\xcd\xa9\x13\xde\xb6\xf6yg\xb9\x9dg\xac\xdf\xa1q,)6\x01'


def test_bytes32_data_registry_via_register_data(deploy_client,
                                                 deployed_contracts,
                                                 deploy_coinbase,
                                                 deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setBytes32,
        target_block=deploy_client.get_block_number() + 40,
    )

    value = 'this is a bytes32 string'
    sig = call.registerData.encoded_abi_signature
    call_data = utils.encode_hex(sig + client_contract.setBytes32.abi_args_signature([value]))

    deploy_client.send_transaction(
        to=call._meta.address,
        data=call_data,
    )

    # FROM: abi.encode_single(abi.process_type('bytes32'), 'this is a bytes32 string')
    assert call.callData() == 'this is a bytes32 string\x00\x00\x00\x00\x00\x00\x00\x00'


def test_bytes_data_registry_via_register_data(deploy_client,
                                               deployed_contracts,
                                               deploy_coinbase,
                                               deploy_future_block_call,
                                               CallLib):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setBytes,
        target_block=deploy_client.get_block_number() + 40,
    )

    value = 'abc'
    sig = call.registerData.encoded_abi_signature
    call_data = utils.encode_hex(sig + client_contract.setBytes.abi_args_signature([value]))

    deploy_client.send_transaction(
        to=call._meta.address,
        data=call_data,
    )

    # FROM: abi.encode_single(abi.process_type('bytes'), 'abc')
    expected = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03abc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    actual = call.callData()
    assert actual == expected


def test_registration_of_many_values_via_register_data(deploy_client,
                                                       deployed_contracts,
                                                       deploy_coinbase,
                                                       deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution

    call = deploy_future_block_call(
        client_contract.setMany,
        target_block=deploy_client.get_block_number() + 40,
    )

    values = (
        1234567890,
        -1234567890,
        987654321,
        '\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13',
        '0xd3cda913deb6f67967b99d67acdfa1712c293601',
        'abcdef',
    )
    sig = call.registerData.encoded_abi_signature
    call_data = utils.encode_hex(sig + client_contract.setMany.abi_args_signature(values))

    deploy_client.send_transaction(
        to=call._meta.address,
        data=call_data,
    )

    expected = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00I\x96\x02\xd2\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xb6i\xfd.\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00:\xdeh\xb1\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd3\xcd\xa9\x13\xde\xb6\xf6yg\xb9\x9dg\xac\xdf\xa1q,)6\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06abcdef\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    actual = call.callData()

    assert expected == actual
