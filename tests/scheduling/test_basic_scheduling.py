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

    target_block = deploy_client.get_block_number() + 300

    scheduling_txn_hash = scheduler.schedule_call(
        client_contract._meta.address,
        client_contract.setBool.encoded_abi_signature,
        target_block,
        1000000,
        value=10 * denoms.ether,
        gas=3000000,
    )
    scheduling_txn = deploy_client.get_transaction_by_hash(scheduling_txn_hash)

    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn_hash)
    call = get_call(scheduling_txn_hash)

    assert call.target_block() == target_block
    assert call.grace_period() == 255
    assert call.suggested_gas() == 1000000
    assert call.base_payment() == denoms.ether
    assert call.base_fee() == 100 * denoms.finney
    assert call.scheduler_address() == deploy_coinbase
    assert call.contract_address() == client_contract._meta.address
    assert call.abi_signature() == client_contract.setBool.encoded_abi_signature
    assert call.anchor_gas_price() == int(scheduling_txn['gasPrice'], 16)
    assert call.suggested_gas() == 1000000
    assert call.bidder() == "0x0000000000000000000000000000000000000000"
    assert call.bid_amount() == 0
    assert call.bidder_deposit() == 0
    assert call.was_successful() is False
    assert call.was_called() is False
    assert call.is_cancelled() is False
