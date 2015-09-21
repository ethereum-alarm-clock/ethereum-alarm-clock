from ethereum import utils

from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction, wait_for_block

from alarm_client.client import (
    ScheduledCall,
    PoolManager,
)


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_scheduled_call_python_object(geth_node, geth_coinbase, rpc_client, deployed_contracts, contracts):
    alarm = deployed_contracts.Alarm
    caller_pool = contracts.CallerPool(alarm.getCallerPoolAddress.call(), rpc_client)
    client_contract = deployed_contracts.PassesUInt

    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, 3)
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)
    txn = rpc_client.get_transaction_by_hash(txn_hash)

    assert client_contract.value.call() == 0

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    owner = '0xd3cda913deb6f67967b99d67acdfa1712c293601'

    wait_for_block(rpc_client, alarm.getCallTargetBlock.call(callKey), 120)
    txn_receipt = wait_for_transaction(alarm._meta.rpc_client, alarm.doCall.sendTransaction(callKey))
    call_txn = rpc_client.get_transaction_by_hash(txn_receipt['transactionHash'])

    pool_manager = PoolManager(caller_pool, block_sage)
    scheduled_call = ScheduledCall(alarm, pool_manager, callKey)

    assert scheduled_call.scheduler_account_balance == alarm.accountBalances.call(client_contract._meta.address)
    assert scheduled_call.target_block == alarm.getCallTargetBlock.call(callKey)
    assert scheduled_call.scheduled_by == client_contract._meta.address
    assert scheduled_call.called_at_block == int(txn_receipt['blockNumber'], 16)
    assert scheduled_call.contract_address == client_contract._meta.address
    assert scheduled_call.base_gas_price == int(txn['gasPrice'], 16)
    assert scheduled_call.gas_price == int(call_txn['gasPrice'], 16)
    assert scheduled_call.gas_used == int(txn_receipt['gasUsed'], 16)
    assert scheduled_call.payout == alarm.accountBalances.call(geth_coinbase) == alarm.getCallPayout.call(callKey)
    assert scheduled_call.fee == alarm.accountBalances.call(owner) == alarm.getCallFee.call(callKey)
    assert scheduled_call.sig == client_contract.doIt.encoded_abi_function_signature == alarm.getCallSignature.call(callKey)
    assert scheduled_call.is_cancelled is False
    assert scheduled_call.was_called is True
    assert scheduled_call.was_successful is True
    assert utils.encode_hex(scheduled_call.data_hash) == 'c2575a0e9e593c00f959f8c92f12db2869c3395a3b0502d05e2516446f71f85b'
