import pytest

from ethereum import abi
from ethereum import utils
from ethereum.tester import TransactionFailed


deploy_contracts = [
    "Scheduler",
    "TestErrors",
]


@pytest.mark.parametrize(
    'pre_drill,depth,contract_depth,should_succeed',
    (
        (0, 0, 1, True),
        (0, 1, 1, True),
        (0, 10, 1, True),
        (0, 5, 5, True),
        (0, 128, 1, True),
        (0, 256, 1, True),
        (0, 1023, 1, False),
    )
)
def test_stack_depth(deploy_client, deployed_contracts,
                     deploy_future_block_call, pre_drill, depth,
                     contract_depth, should_succeed):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestErrors
    client_contract.reset()

    call = deploy_future_block_call(
        client_contract.doStackExtension,
        call_data=client_contract.doStackExtension.abi_args_signature([contract_depth]),
        require_depth=depth,
    )
    assert call.requiredStackDepth() == depth

    deploy_client.wait_for_block(call.targetBlock())

    assert client_contract.value() is False

    if should_succeed:
        call_txn_hash = client_contract.proxyCall(call._meta.address, pre_drill)
        call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

        assert call.wasCalled() is True
        assert client_contract.value() is True
    else:
        client_contract.proxyCall(call._meta.address, pre_drill)

        assert call.wasCalled() is False
        assert client_contract.value() is False
