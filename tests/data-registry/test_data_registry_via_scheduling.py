import pytest

from ethereum import abi
from ethereum import utils


deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestDataRegistry",
    "TestCallExecution",
]


def test_int_data_registry_via_scheduling(deploy_client, deployed_contracts,
                                          deploy_future_block_call, get_call,
                                          denoms):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    value = -1234567890

    scheduling_txn_hash = scheduler.scheduleCall(
        client_contract.setInt.encoded_abi_signature,
        client_contract.setInt.abi_args_signature([value]),
        value=2 * denoms.ether,
    )

    call = get_call(scheduling_txn_hash)

    # FROM: abi.encode_single(abi.process_type('int256'), value)
    assert call.callData() == '\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xb6i\xfd.'


def test_uint_data_registry_via_scheduling(deploy_client, deployed_contracts,
                                           deploy_future_block_call, denoms, get_call):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    # 2 ** 128 + 1
    value = 340282366920938463463374607431768211457

    scheduling_txn_hash = scheduler.scheduleCall(
        client_contract.setUInt.encoded_abi_signature,
        client_contract.setUInt.abi_args_signature([value]),
        value=2 * denoms.ether,
    )

    call = get_call(scheduling_txn_hash)

    # FROM: abi.encode_single(abi.process_type('uint256'), value)
    assert call.callData() == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'


def test_address_data_registry_via_scheduling(deploy_client, get_call,
                                              deployed_contracts,
                                              deploy_coinbase, denoms,
                                              deploy_future_block_call):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    value = '0xd3cda913deb6f67967b99d67acdfa1712c293601'

    scheduling_txn_hash = scheduler.scheduleCall(
        client_contract.setAddress.encoded_abi_signature,
        client_contract.setAddress.abi_args_signature([value]),
        value=2 * denoms.ether,
    )

    call = get_call(scheduling_txn_hash)

    # FROM: abi.encode_single(abi.process_type('address'), 'd3cda913deb6f67967b99d67acdfa1712c293601')
    assert call.callData() == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd3\xcd\xa9\x13\xde\xb6\xf6yg\xb9\x9dg\xac\xdf\xa1q,)6\x01'


def test_bytes32_data_registry_via_scheduling(deploy_client, get_call,
                                              deployed_contracts,
                                              deploy_coinbase, denoms,
                                              deploy_future_block_call):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    value = 'this is a bytes32 string'

    scheduling_txn_hash = scheduler.scheduleCall(
        client_contract.setBytes32.encoded_abi_signature,
        client_contract.setBytes32.abi_args_signature([value]),
        value=2 * denoms.ether,
    )

    call = get_call(scheduling_txn_hash)

    # FROM: abi.encode_single(abi.process_type('bytes32'), 'this is a bytes32 string')
    assert call.callData() == 'this is a bytes32 string\x00\x00\x00\x00\x00\x00\x00\x00'


def test_bytes_data_registry_via_scheduling(deploy_client, deployed_contracts,
                                            deploy_coinbase, denoms, get_call,
                                            deploy_future_block_call, CallLib):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    value = 'abc'

    scheduling_txn_hash = scheduler.scheduleCall(
        client_contract.setBytes.encoded_abi_signature,
        client_contract.setBytes.abi_args_signature([value]),
        value=2 * denoms.ether,
    )

    call = get_call(scheduling_txn_hash)

    # FROM: abi.encode_single(abi.process_type('bytes'), 'abc')
    expected = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03abc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    actual = call.callData()
    assert actual == expected


def test_registration_of_many_values_via_scheduling(deploy_client, get_call,
                                                    deployed_contracts,
                                                    deploy_coinbase,
                                                    deploy_future_block_call,
                                                    denoms):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    values = (
        1234567890,
        -1234567890,
        987654321,
        '\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13',
        '0xd3cda913deb6f67967b99d67acdfa1712c293601',
        'abcdef',
    )
    scheduling_txn_hash = scheduler.scheduleCall(
        client_contract.setMany.encoded_abi_signature,
        client_contract.setMany.abi_args_signature(values),
        value=2 * denoms.ether,
    )

    call = get_call(scheduling_txn_hash)

    expected = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00I\x96\x02\xd2\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xb6i\xfd.\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00:\xdeh\xb1\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd3\xcd\xa9\x13\xde\xb6\xf6yg\xb9\x9dg\xac\xdf\xa1q,)6\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06abcdef\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    actual = call.callData()

    assert expected == actual
