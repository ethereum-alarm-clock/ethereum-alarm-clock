deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestCallExecution",
]


def test_execution_of_call_with_single_bool(deploy_client, deployed_contracts,
                                            deploy_future_block_call, get_call):
    client_contract = deployed_contracts.TestCallExecution
    scheduler = deployed_contracts.Scheduler

    call = deploy_future_block_call(client_contract.noop)
    deploy_client.wait_for_block(call.targetBlock())

    assert client_contract.v_bool() is False

    call_txn_hash = call.execute()
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    assert call.wasCalled() is True
    assert call.wasSuccessful() is True

    expected = scheduler.getMinimumCallGas()
    actual = int(call_txn_receipt['gasUsed'], 16)

    assert actual < expected
    assert expected - actual < 21000
