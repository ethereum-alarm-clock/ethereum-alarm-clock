import pytest


@pytest.fixture()
def geth_node_config(monkeypatch):
    monkeypatch.setenv('DEPLOY_MAX_WAIT', '20')
    monkeypatch.setenv('DEPLOY_WAIT_FOR_BLOCK', '1')
    monkeypatch.setenv('DEPLOY_WAIT_FOR_BLOCK_MAX_WAIT', '180')
    # Deploy contracts using the RPC client
    monkeypatch.setenv('DEPLOY_CLIENT_TYPE', 'rpc')

    monkeypatch.setenv('GETH_MAX_WAIT', '45')


@pytest.fixture(autouse=True, scope="module")
def contract_deployment_config(populus_config):
    populus_config.deploy_contracts = [
        "Alarm",
    ]
