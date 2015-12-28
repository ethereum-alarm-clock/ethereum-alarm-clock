deploy_contracts = [
    "Scheduler",
]


def test_canary_is_alive_on_initial_deploy(canary):
    assert canary.callContractAddress() == "0x0000000000000000000000000000000000000000"
    assert canary.isAlive() is False
