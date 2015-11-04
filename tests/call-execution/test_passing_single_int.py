import pytest

from populus.contracts import (
    deploy_contract,
    link_contract_dependency,
)
from populus.utils import (
    get_contract_address_from_txn,
)


deploy_contracts = [
    "CallLib",
    "TestCallExecution",
    "TestDataRegistry",
]


import pytest


@pytest.fixture
def FutureBlockCall(contracts, deployed_contracts):
    return link_contract_dependency(contracts.FutureBlockCall, deployed_contracts.CallLib)


def deploy_future_block_call(deploy_client,



def test_executing_scheduled_call_with_int(deploy_client, deployed_contracts, deploy_coinbase, FutureBlockCall):
    client_contract = deployed_contracts.TestCallExecution
    data_register = deployed_contracts.TestDataRegistry

    deposit_amount = deploy_client.get_max_gas() * deploy_client.get_gas_price() * 20

    deploy_txn = deploy_contract(
        deploy_client,
        FutureBlockCall,
        constructor_args=(
            deploy_coinbase,
            100,
            164,
            client_contract._meta.address,
            client_contract.setInt.encoded_abi_signature,
            100000,
            1,
            1,
        ),
        value=deposit_amount,
    )

    addr = get_contract_address_from_txn(deploy_client, deploy_txn)
    call = contracts.FutureBlockCall(addr, deploy_client)

    data_register.registerInt(call._meta.address, 1234567890)

    assert client_contract.v_int() == 0

    call_txn_hash = call.execute()
    deploy_client.wait_for_transaction(call_txn_hash)

    assert client_contract.v_int() == 1234567890
