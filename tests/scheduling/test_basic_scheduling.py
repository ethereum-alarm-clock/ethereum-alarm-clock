deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestCallExecution",
    "TestDataRegistry",
]


def test_basic_call_scheduling(deploy_client, deployed_contracts,
                               deploy_future_block_call, denoms,
                               FutureBlockCall, CallLib, SchedulerLib,
                               get_call, get_execution_data, deploy_coinbase):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    targetBlock = deploy_client.get_block_number() + 255 + 10 + 40

    scheduling_txn_hash = scheduler.scheduleCall(
        client_contract._meta.address,
        client_contract.setBool.encoded_abi_signature,
        targetBlock,
        1000000,
        value=10 * denoms.ether,
        gas=3000000,
    )
    scheduling_txn = deploy_client.get_transaction_by_hash(scheduling_txn_hash)

    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn_hash)
    call = get_call(scheduling_txn_hash)

    # Sanity check for all of the queriable call values.
    assert call.targetBlock() == targetBlock
    assert call.gracePeriod() == 255
    assert call.suggestedGas() == 1000000
    assert call.basePayment() == denoms.ether
    assert call.baseFee() == 100 * denoms.finney
    assert call.schedulerAddress() == deploy_coinbase
    assert call.contractAddress() == client_contract._meta.address
    assert call.abiSignature() == client_contract.setBool.encoded_abi_signature
    assert call.anchorGasPrice() == int(scheduling_txn['gasPrice'], 16)
    assert call.claimer() == "0x0000000000000000000000000000000000000000"
    assert call.claimAmount() == 0
    assert call.claimerDeposit() == 0
    assert call.wasSuccessful() is False
    assert call.wasCalled() is False
    assert call.isCancelled() is False
