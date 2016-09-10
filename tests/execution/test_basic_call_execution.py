import pytest

from web3.utils.string import force_text
from web3.utils.encoding import decode_hex


def test_execution_of_call_with_single_bool(chain, deploy_fbc):
    client_contract = chain.get_contract('TestCallExecution')

    fbc = deploy_fbc(client_contract, method_name='setBool')
    chain.wait.for_block(fbc.call().targetBlock())

    assert client_contract.call().v_bool() is False

    call_txn_hash = fbc.transact().execute()
    chain.wait.for_receipt(call_txn_hash)

    assert client_contract.call().v_bool() is True


@pytest.mark.parametrize(
    'fn_name,fn_args,init_value,lookup_fn',
    (
        ('setInt', [-1234567890], 0, 'v_int'),
        ('setUInt', [1234567890], 0, 'v_uint'),
        (
            'setAddress',
            ['0xd3cda913deb6f67967b99d67acdfa1712c293601'],
            '0x0000000000000000000000000000000000000000',
            'v_address',
        ),
        (
            'setBytes32',
            [force_text(decode_hex('000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f'))],
            force_text(decode_hex('00' * 32)),
            'v_bytes32',
        ),
        (
            'setBytes',
            ['abcdefg'],
            '',
            'v_bytes',
        ),
    ),
)
def test_execution_of_call_with_args(chain,
                                     deploy_fbc,
                                     fn_name,
                                     fn_args,
                                     init_value,
                                     lookup_fn):
    client_contract = chain.get_contract('TestCallExecution')

    fbc = deploy_fbc(
        client_contract,
        method_name=fn_name,
        arguments=fn_args,
    )
    chain.wait.for_block(fbc.call().targetBlock())

    assert getattr(client_contract.call(), lookup_fn)() == init_value

    execute_txn_hash = fbc.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert getattr(client_contract.call(), lookup_fn)() == fn_args[0]


def test_execution_of_call_with_many_values(chain, deploy_fbc):
    client_contract = chain.get_contract('TestCallExecution')

    values = (
        1234567890,
        -1234567890,
        987654321,
        '\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13',
        'd3cda913deb6f67967b99d67acdfa1712c293601',
        'abcdefg',
    )

    fbc = deploy_fbc(
        client_contract,
        method_name='setMany',
        arguments=values,
    )
    chain.wait.for_block(fbc.call().targetBlock())

    assert client_contract.call().vm_a() == 0
    assert client_contract.call().vm_b() == 0
    assert client_contract.call().vm_c() == 0
    assert client_contract.call().vm_d() == decode_hex('00' * 32)
    assert client_contract.call().vm_e() == '0x0000000000000000000000000000000000000000'
    assert client_contract.call().vm_f() == ''

    call_txn_hash = fbc.transact().execute()
    chain.wait.for_receipt(call_txn_hash)

    assert client_contract.call().vm_a() == values[0]
    assert client_contract.call().vm_b() == values[1]
    assert client_contract.call().vm_c() == values[2]
    assert client_contract.call().vm_d() == values[3]
    assert client_contract.call().vm_e() == '0xd3cda913deb6f67967b99d67acdfa1712c293601'
    assert client_contract.call().vm_f() == values[5]
