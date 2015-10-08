import pytest


@pytest.fixture(autouse=True)
def deployed_contracts_config(monkeypatch):
    monkeypatch.setenv('DEPLOY_MAX_WAIT', '20')
    monkeypatch.setenv('DEPLOY_WAIT_FOR_BLOCK', '1')
    monkeypatch.setenv('DEPLOY_WAIT_FOR_BLOCK_MAX_WAIT', '180')
    # Deploy contracts using the RPC client
    monkeypatch.setenv('DEPLOY_CLIENT_TYPE', 'rpc')


@pytest.fixture(autouse=True)
def geth_node_config(monkeypatch):
    monkeypatch.setenv('GETH_MAX_WAIT', '45')


def _alarm_constructor_args(deployed_contracts):
    grove = deployed_contracts['Grove']
    return (grove._meta.address,)


@pytest.fixture(autouse=True, scope="module")
def contract_deployment_config(populus_config):
    populus_config.deploy_dependencies = {
        "Alarm": set(["Grove"]),
    }
    populus_config.deploy_constructor_args = {
        "Alarm": _alarm_constructor_args,
    }
    populus_config.deploy_contracts = [
        "Alarm",
        "Grove",
    ]
