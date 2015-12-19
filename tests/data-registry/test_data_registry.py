import pytest

from ethereum import utils


deploy_contracts = [
    "CallLib",
    "TestDataRegistry",
    "TestCallExecution",
]


def test_int_data_registry(deploy_client, deployed_contracts,
                           deploy_future_block_call):
    data_register = deployed_contracts.TestDataRegistry

    if data_register.wasSuccessful() != 0:
        deploy_client.wait_for_transaction(data_register.reset())

    call = deploy_future_block_call(
        data_register.wasSuccessful,
        scheduler_address=data_register._meta.address,
    )

    assert data_register.wasSuccessful() == 0

    value = -1234567890

    data_register.registerInt(call._meta.address, value)

    assert data_register.wasSuccessful() == 1

    # FROM: abi.encode_single(abi.process_type('int256'), value)
    assert call.callData() == '\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xb6i\xfd.'


def test_uint_data_registry(deploy_client, deployed_contracts,
                            deploy_future_block_call):
    data_register = deployed_contracts.TestDataRegistry

    if data_register.wasSuccessful() != 0:
        deploy_client.wait_for_transaction(data_register.reset())

    call = deploy_future_block_call(
        data_register.wasSuccessful,
        scheduler_address=data_register._meta.address,
    )

    assert data_register.wasSuccessful() == 0

    value = 1234567890123456789012345678901234567890

    data_register.registerUInt(call._meta.address, value)

    assert data_register.wasSuccessful() == 1

    # FROM: abi.encode_single(abi.process_type('uint256'), value)
    assert call.callData() == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xa0\xc9 u\xc0\xdb\xf3\xb8\xac\xbc_\x96\xce?\n\xd2'


def test_address_data_registry(deploy_client,
                               deployed_contracts,
                               deploy_coinbase,
                               deploy_future_block_call):
    data_register = deployed_contracts.TestDataRegistry

    if data_register.wasSuccessful() != 0:
        deploy_client.wait_for_transaction(data_register.reset())

    call = deploy_future_block_call(
        data_register.wasSuccessful,
        scheduler_address=data_register._meta.address,
    )

    assert data_register.wasSuccessful() == 0

    value = '0xd3cda913deb6f67967b99d67acdfa1712c293601'

    data_register.registerAddress(call._meta.address, value)

    assert data_register.wasSuccessful() == 1

    # FROM: abi.encode_single(abi.process_type('address'), 'd3cda913deb6f67967b99d67acdfa1712c293601')
    assert call.callData() == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd3\xcd\xa9\x13\xde\xb6\xf6yg\xb9\x9dg\xac\xdf\xa1q,)6\x01'


def test_bytes32_data_registry(deploy_client,
                               deployed_contracts,
                               deploy_coinbase,
                               deploy_future_block_call):
    data_register = deployed_contracts.TestDataRegistry

    if data_register.wasSuccessful() != 0:
        deploy_client.wait_for_transaction(data_register.reset())

    call = deploy_future_block_call(
        data_register.wasSuccessful,
        scheduler_address=data_register._meta.address,
    )

    assert data_register.wasSuccessful() == 0

    value = 'this is a bytes32 string'

    data_register.registerBytes32(call._meta.address, value)

    assert data_register.wasSuccessful() == 1

    # FROM: abi.encode_single(abi.process_type('bytes32'), 'this is a bytes32 string')
    assert call.callData() == 'this is a bytes32 string\x00\x00\x00\x00\x00\x00\x00\x00'


def test_bytes_data_registry(deploy_client,
                             deployed_contracts,
                             deploy_coinbase,
                             deploy_future_block_call,
                             CallLib):
    data_register = deployed_contracts.TestDataRegistry

    if data_register.wasSuccessful() != 0:
        deploy_client.wait_for_transaction(data_register.reset())

    call = deploy_future_block_call(
        data_register.wasSuccessful,
        scheduler_address=data_register._meta.address,
    )

    assert data_register.wasSuccessful() == 0

    value = 'abc'

    txn_hash = data_register.registerBytes(call._meta.address, value)
    txn_receipt = deploy_client.wait_for_transaction(txn_hash)

    assert data_register.wasSuccessful() == 1

    # FROM: abi.encode_single(abi.process_type('bytes'), 'abc')
    expected = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03abc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    actual = call.callData()
    assert actual == expected


def test_registration_of_many_values(deploy_client,
                                     deployed_contracts,
                                     deploy_coinbase,
                                     deploy_future_block_call):
    data_register = deployed_contracts.TestDataRegistry

    if data_register.wasSuccessful() != 0:
        deploy_client.wait_for_transaction(data_register.reset())

    call = deploy_future_block_call(
        data_register.wasSuccessful,
        scheduler_address=data_register._meta.address,
    )

    assert data_register.wasSuccessful() == 0

    values = (
        1234567890,
        -1234567890,
        987654321,
        '\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13',
        '0xd3cda913deb6f67967b99d67acdfa1712c293601',
        'abcdef',
    )
    data_register.registerMany(call._meta.address, *values)

    expected ='\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00I\x96\x02\xd2\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xb6i\xfd.\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00:\xdeh\xb1\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd3\xcd\xa9\x13\xde\xb6\xf6yg\xb9\x9dg\xac\xdf\xa1q,)6\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06abcdef\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    actual = call.callData()

    assert expected == actual
