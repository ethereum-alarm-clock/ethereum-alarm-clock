import pytest

from web3.utils.encoding import (
    encode_hex,
    decode_hex,
)


@pytest.mark.parametrize(
    'fn_name,fn_args',
    (
        ('setInt', [-1234567890]),
        ('setUInt', [2**255 - 1]),
        ('setAddress', ['0xd3cda913deb6f67967b99d67acdfa1712c293601']),
        ('setBytes32', ['this is a bytes32 string']),
        ('setBytes', ['this is a byte string that is longer than 32 bytes']),
        (
            'setMany',
            (
                1234567890,
                -1234567890,
                987654321,
                '\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13',
                '0xd3cda913deb6f67967b99d67acdfa1712c293601',
                'abcdef',
            ),
        ),
    ),
)
def test_data_registry_via_scheduling(chain,
                                      web3,
                                      get_scheduled_fbc,
                                      denoms,
                                      fn_name,
                                      fn_args):
    scheduler = chain.get_contract('Scheduler')
    client_contract = chain.get_contract('TestCallExecution')

    _, sig, _ = client_contract._get_function_info(fn_name, fn_args)
    call_data = client_contract.encodeABI(fn_name, fn_args)

    scheduling_txn_hash = scheduler.transact({
        'value': 2 * denoms.ether,
    }).scheduleCall(
        abiSignature=decode_hex(sig),
        callData=decode_hex(call_data),
    )

    fbc = get_scheduled_fbc(scheduling_txn_hash)

    assert encode_hex(fbc.call().callData()) == call_data
