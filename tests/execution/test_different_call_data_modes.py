from web3.utils.encoding import decode_hex


def test_no_signature_or_calldata(chain, web3, deploy_fbc):
    client_contract = chain.get_contract('TestCallExecution')

    fbc = deploy_fbc(client_contract)
    chain.wait.for_block(fbc.call().targetBlock())

    assert client_contract.v_bool() == ""

    execute_txn_hash = fbc.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert client_contract.call().v_bytes() == ""
    assert fbc.call().wasCalled() is True
    assert fbc.call().wasSuccessful() is True


def test_only_signature(chain, web3, deploy_fbc):
    client_contract = chain.get_contract('TestCallExecution')

    _, sig, _ = client_contract._get_function_info('setBool')

    fbc = deploy_fbc(
        client_contract,
        abi_signature=decode_hex(sig),
    )
    chain.wait.for_block(fbc.call().targetBlock())

    assert client_contract.call().v_bool() is False

    execute_txn_hash = fbc.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert client_contract.call().v_bool() is True
    assert fbc.call().wasCalled() is True
    assert fbc.call().wasSuccessful() is True


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
