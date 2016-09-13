def test_canary_cannot_be_double_initialized(chain, deploy_canary):
    canary = deploy_canary()

    assert canary.call().isAlive() is False

    first_init_txn_hash = canary.transact().initialize()
    chain.wait.for_receipt(first_init_txn_hash)

    assert canary.call().isAlive() is True

    fbc_address = canary.call().callContractAddress()
    assert fbc_address != "0x0000000000000000000000000000000000000000"

    second_init_txn_hash = canary.transact().initialize()
    chain.wait.for_receipt(second_init_txn_hash)

    assert canary.call().isAlive() is True
    # assert that the address hasn't changed
    assert fbc_address == canary.call().callContractAddress()
