from web3.utils.encoding import decode_hex


def test_no_signature_or_calldata(chain, web3, deploy_fbc):
    client_contract = chain.get_contract('TestCallExecution')

    fbc = deploy_fbc(client_contract)
    chain.wait.for_block(fbc.call().targetBlock())

    execute_txn_hash = fbc.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert fbc.call().wasCalled() is True
    assert fbc.call().wasSuccessful() is True


def test_only_signature(chain, deploy_fbc):
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


def test_only_call_data(chain, deploy_fbc):
    client_contract = chain.get_contract('TestCallExecution')

    call_data = client_contract._encode_transaction_data('setUInt', [12345])

    fbc = deploy_fbc(
        client_contract,
        call_data=decode_hex(call_data),
    )
    chain.wait.for_block(fbc.call().targetBlock())

    assert client_contract.call().v_uint() == 0

    execute_txn_hash = fbc.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert client_contract.call().v_uint() == 12345


def test_both_signature_and_call_data(chain, deploy_fbc):
    client_contract = chain.get_contract('TestCallExecution')

    _, sig, _ = client_contract._get_function_info('setUInt', [12345])
    call_data = client_contract.encodeABI('setUInt', [12345])

    fbc = deploy_fbc(
        client_contract,
        call_data=decode_hex(call_data),
        abi_signature=decode_hex(sig),
    )
    chain.wait.for_block(fbc.call().targetBlock())

    assert client_contract.call().v_uint() == 0

    execute_txn_hash = fbc.transact().execute()
    chain.wait.for_receipt(execute_txn_hash)

    assert client_contract.call().v_uint() == 12345
