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
    return link_contract_dependency(
        link_contract_dependency(contracts.FutureBlockCall, deployed_contracts.CallLib),
        deployed_contracts.AccountingLib,
    )


@pytest.fixture
def deploy_future_block_call(deploy_client, FutureBlockCall, deploy_coinbase):
    from populus.contracts import (
        deploy_contract,
    )
    from populus.utils import (
        get_contract_address_from_txn,
    )

    def _deploy_future_block_call(contract_function, scheduler_address=None,
                                  target_block=None, grace_period=64,
                                  suggested_gas=100000, payment=1, fee=1,
                                  endowment=None):
        if endowment is None:
            endowment = deploy_client.get_max_gas() * deploy_client.get_gas_price() + payment + fee

        if target_block is None:
            target_block = deploy_client.get_block_number() + 40

        if scheduler_address is None:
            scheduler_address = deploy_coinbase

        deploy_txn_hash = deploy_contract(
            deploy_client,
            FutureBlockCall,
            constructor_args=(
                scheduler_address,
                target_block,
                grace_period,
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


@pytest.fixture(scope="module")
def CallLib(deployed_contracts):
    return deployed_contracts.CallLib


@pytest.fixture(scope="module")
def SchedulerLib(deployed_contracts):
    return deployed_contracts.SchedulerLib


@pytest.fixture(scope="session")
def denoms():
    from ethereum.utils import denoms as ether_denoms
    return ether_denoms


@pytest.fixture(scope="module")
def get_call(SchedulerLib, FutureBlockCall, deploy_client):
    def _get_call(txn_hash):
        call_scheduled_logs = SchedulerLib.CallScheduled.get_transaction_logs(txn_hash)
        assert len(call_scheduled_logs) == 1
        call_scheduled_data = SchedulerLib.CallScheduled.get_log_data(call_scheduled_logs[0])

        call_address = call_scheduled_data['call_address']
        call = FutureBlockCall(call_address, deploy_client)
        return call
    return _get_call


@pytest.fixture(scope="module")
def get_execution_data(CallLib):
    def _get_execution_data(txn_hash):
        execution_logs = CallLib.CallExecuted.get_transaction_logs(txn_hash)
        assert len(execution_logs) == 1
        execution_data = CallLib.CallExecuted.get_log_data(execution_logs[0])

        return execution_data
    return _get_execution_data
