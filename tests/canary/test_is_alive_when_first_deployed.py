def test_canary_is_alive_on_initial_deploy(deploy_canary):
    canary = deploy_canary()
    assert canary.call().callContractAddress() == "0x0000000000000000000000000000000000000000"
    assert canary.call().isAlive() is False
