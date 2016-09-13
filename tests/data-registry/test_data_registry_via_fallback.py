import pytest

from web3.utils.encoding import (
    encode_hex,
)


@pytest.mark.parametrize(
    'fn_name,fn_args',
    (
        ('setInt', [-1234567890]),
        ('setUInt', [1234567890123456789012345678901234567890]),
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
    )
)
def test_data_registry_via_fallback(chain, web3, deploy_fbc, fn_name, fn_args):
    client_contract = chain.get_contract('TestCallExecution')

    fbc = deploy_fbc(
        client_contract,
        method_name=fn_name,
        call_data="",
        target_block=web3.eth.blockNumber + 300,
    )

    call_data = client_contract._encode_transaction_data(fn_name, fn_args)

    web3.eth.sendTransaction({
        'to': fbc.address,
        'data': call_data,
    })

    # FROM: abi.encode_single(abi.process_type('int256'), value)
    assert encode_hex(fbc.call().callData()) == call_data
