deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestCallExecution",
]


MEASURED_VALUE = 80000


def test_minimum_call_gas(deploy_client, deployed_contracts,
                          deploy_future_block_call, get_call, denoms,
                          deploy_coinbase):
    client_contract = deployed_contracts.TestCallExecution
    scheduler = deployed_contracts.Scheduler

    target_block = deploy_client.get_block_number() + 400

    scheduling_txn_hash = scheduler.scheduleCall(
        client_contract._meta.address,
        client_contract.setBool.encoded_abi_signature,
        target_block,
        value=10 * denoms.ether,
        gas=3000000,
    )
    scheduling_txn = deploy_client.get_transaction_by_hash(scheduling_txn_hash)

    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn_hash)
    call = get_call(scheduling_txn_hash)

    deploy_client.wait_for_block(call.firstClaimBlock() + 250)

    claim_txn_hash = call.claim(value=10 * denoms.ether)
    claim_txn_receipt = deploy_client.wait_for_transaction(claim_txn_hash)

    deploy_client.wait_for_block(call.targetBlock())

    assert call.claimer() == deploy_coinbase
    assert client_contract.v_bool() is False

    call_txn_hash = call.execute()
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)

    assert call.wasCalled() is True
    assert call.wasSuccessful() is True

    actual = int(call_txn_receipt['gasUsed'], 16)

    assert actual < MEASURED_VALUE
    assert MEASURED_VALUE - actual < 10000
    assert actual * 2 < scheduler.getMinimumCallGas()
