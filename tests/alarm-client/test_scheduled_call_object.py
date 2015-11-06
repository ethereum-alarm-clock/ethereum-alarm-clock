from ethereum import utils

from eth_alarm_client import (
    ScheduledCall,
    PoolManager,
)


deploy_contracts = [
    "Scheduler",
    "TestCallExecution",
]


def test_scheduled_call_python_object(deploy_client, deployed_contracts,
                                      contracts, deploy_coinbase, get_call,
                                      get_execution_data, denoms):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    target_block = deploy_client.get_block_number() + 45

    scheduling_txn_hash = scheduler.scheduleCall(
        client_contract._meta.address,
        client_contract.setBool.encoded_abi_signature,
        target_block,
        1000000,
        value=10 * denoms.ether,
        gas=3000000,
    )
    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn_hash)
    scheduling_txn = deploy_client.get_transaction_by_hash(scheduling_txn_hash)

    call = get_call(scheduling_txn_hash)
    call_address = call._meta.address

    scheduled_call = ScheduledCall(scheduler, call_address)
    block_sage = scheduled_call.block_sage

    assert client_contract.v_bool() is False

    owner = '0xd3cda913deb6f67967b99d67acdfa1712c293601'

    deploy_client.wait_for_block(
        call.targetBlock(), block_sage.estimated_time_to_block(call.targetBlock()),
    )

    assert scheduled_call.balance == deploy_client.get_balance(call_address)
    assert scheduled_call.has_been_suicided is False
    assert scheduled_call.target_block == target_block
    assert scheduled_call.scheduled_by == deploy_coinbase
    assert scheduled_call.contract_address == client_contract._meta.address
    assert scheduled_call.anchor_gas_price == int(scheduling_txn['gasPrice'], 16)
    assert scheduled_call.abi_signature == client_contract.setBool.encoded_abi_signature

    call_txn_hash = scheduler.execute(call_address)
    call_txn_receipt = deploy_client.wait_for_transaction(call_txn_hash)
    call_txn = deploy_client.get_transaction_by_hash(call_txn_hash)

    execute_data = get_execution_data(call_txn_hash)

    assert client_contract.v_bool() is True

    assert scheduled_call.has_been_suicided is True
