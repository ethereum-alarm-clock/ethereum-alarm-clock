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
        "Scheduler",
        "CallLib",
    ]


@pytest.fixture(scope="module")
def FutureBlockCall(contracts, deployed_contracts):
    from populus.contracts import (
        link_contract_dependency,
    )
    return link_contract_dependency(contracts.FutureBlockCall, deployed_contracts.CallLib)


@pytest.fixture
def deploy_future_block_call(deploy_client, FutureBlockCall, deploy_coinbase):
    from populus.contracts import (
        deploy_contract,
    )
    from populus.utils import (
        get_contract_address_from_txn,
    )

    def _deploy_future_block_call(contract_function, target_block=None,
                                  grace_period=64, suggested_gas=100000,
                                  payment=1, fee=1, endowment=None):
        if endowment is None:
            endowment = deploy_client.get_max_gas() * deploy_client.get_gas_price() + payment + fee

        if target_block is None:
            target_block = deploy_client.get_block_number() + 40

        deploy_txn_hash = deploy_contract(
            deploy_client,
            FutureBlockCall,
            constructor_args=(
                deploy_coinbase,
                target_block,
                target_block + grace_period,
                contract_function._contract._meta.address,
                contract_function.encoded_abi_signature,
                suggested_gas,
                payment,
                fee,
            ),
            gas=int(deploy_client.get_max_gas() * 0.95),
            value=endowment,
        )

        call_address = get_contract_address_from_txn(deploy_client, deploy_txn_hash, 180)
        call = FutureBlockCall(call_address, deploy_client)
        return call
    return _deploy_future_block_call
