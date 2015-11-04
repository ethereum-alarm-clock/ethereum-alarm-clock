import pytest


deploy_contracts = [
    "CallLib",
    "TestCallExecution",
    "TestDataRegistry",
]


#def test_execution_of_call_with_single_int(deploy_client, deployed_contracts,
#                                           deploy_future_block_call):
#    client_contract = deployed_contracts.TestCallExecution
#    data_register = deployed_contracts.TestDataRegistry
#
#    call = deploy_future_block_call(client_contract.setInt)
#
#    data_register.registerInt(call._meta.address, -1234567890)
#
#    assert client_contract.v_int() == 0
#
#    call_txn_hash = call.execute()
#    deploy_client.wait_for_transaction(call_txn_hash)
#
#    assert client_contract.v_int() == -1234567890
#
#
#def test_execution_of_call_with_single_uint(deploy_client, deployed_contracts,
#                                            deploy_future_block_call):
#    client_contract = deployed_contracts.TestCallExecution
#    data_register = deployed_contracts.TestDataRegistry
#
#    call = deploy_future_block_call(client_contract.setUInt)
#
#    data_register.registerUInt(call._meta.address, 1234567890)
#
#    assert client_contract.v_uint() == 0
#
#    call_txn_hash = call.execute()
#    deploy_client.wait_for_transaction(call_txn_hash)
#
#    assert client_contract.v_uint() == 1234567890
#
#
#def test_execution_of_call_with_single_address(deploy_client,
#                                               deployed_contracts,
#                                               deploy_coinbase,
#                                               deploy_future_block_call):
#    client_contract = deployed_contracts.TestCallExecution
#    data_register = deployed_contracts.TestDataRegistry
#
#    call = deploy_future_block_call(client_contract.setAddress)
#
#    data_register.registerAddress(call._meta.address, deploy_coinbase)
#
#    assert client_contract.v_address() == '0x0000000000000000000000000000000000000000'
#
#    call_txn_hash = call.execute()
#    deploy_client.wait_for_transaction(call_txn_hash)
#
#    assert client_contract.v_address() == deploy_coinbase
#
#
#def test_execution_of_call_with_single_bytes32(deploy_client,
#                                               deployed_contracts,
#                                               deploy_coinbase,
#                                               deploy_future_block_call):
#    client_contract = deployed_contracts.TestCallExecution
#    data_register = deployed_contracts.TestDataRegistry
#
#    call = deploy_future_block_call(client_contract.setBytes32)
#
#    value = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f'
#    data_register.registerBytes(call._meta.address, value)
#
#    assert client_contract.v_bytes32() is None
#
#    call_txn_hash = call.execute()
#    deploy_client.wait_for_transaction(call_txn_hash)
#
#    assert client_contract.v_bytes32() == value


def test_execution_of_call_with_many_values(geth_node_config, geth_node, deploy_client,
                                            deployed_contracts,
                                            deploy_coinbase,
                                            deploy_future_block_call):
    client_contract = deployed_contracts.TestCallExecution
    data_register = deployed_contracts.TestDataRegistry

    call = deploy_future_block_call(client_contract.setMany)

    values = (
        1234567890,
        -1234567890,
        987654321,
        '\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13',
        deploy_coinbase,
        (
            '\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff'
        ),
    )
    data_register.registerMany(call._meta.address, *values)

    assert client_contract.vm_a() == 0
    assert client_contract.vm_b() == 0
    assert client_contract.vm_c() == 0
    assert client_contract.vm_d() == None
    assert client_contract.vm_e() == '0x0000000000000000000000000000000000000000'
    assert client_contract.vm_f() == ''

    call_txn_hash = call.execute()
    deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.vm_a() == values[0]
    assert client_contract.vm_b() == values[1]
    assert client_contract.vm_c() == values[2]
    assert client_contract.vm_d() == values[3]
    assert client_contract.vm_e() == values[4]
    assert client_contract.vm_f() == values[5]
