from ethereum import utils

from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction

from eth_alarm_client import (
    ScheduledCall,
    PoolManager,
)


deploy_contracts = [
    "Alarm",
    "PassesUInt",
]


def test_scheduled_call_python_object(deploy_client, deployed_contracts, contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.PassesUInt

    coinbase = deploy_client.get_coinbase()

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, 3)
    wait_for_transaction(deploy_client, txn_hash)
    txn = deploy_client.get_transaction_by_hash(txn_hash)

    assert client_contract.value() == 0

    call_key = alarm.getLastCallKey()
    assert call_key is not None

    owner = '0xd3cda913deb6f67967b99d67acdfa1712c293601'

    deploy_client.wait_for_block(alarm.getCallTargetBlock(call_key), 120)
    txn_receipt = wait_for_transaction(deploy_client, alarm.doCall.sendTransaction(call_key))
    call_txn = deploy_client.get_transaction_by_hash(txn_receipt['transactionHash'])

    scheduled_call = ScheduledCall(alarm, call_key)

    assert scheduled_call.scheduler_account_balance == alarm.getAccountBalance(client_contract._meta.address)
    assert scheduled_call.target_block == alarm.getCallTargetBlock(call_key)
    assert scheduled_call.scheduled_by == client_contract._meta.address
    assert scheduled_call.called_at_block == int(txn_receipt['blockNumber'], 16)
    assert scheduled_call.contract_address == client_contract._meta.address
    assert scheduled_call.base_gas_price == int(txn['gasPrice'], 16)
    assert scheduled_call.gas_price == int(call_txn['gasPrice'], 16)

    actual_gas_used = int(txn_receipt['gasUsed'], 16)

    assert scheduled_call.gas_used >= actual_gas_used

    gas_diff = abs(scheduled_call.gas_used - actual_gas_used)
    assert gas_diff in {0, 64}

    assert scheduled_call.payout == alarm.getAccountBalance(coinbase) == alarm.getCallPayout(call_key)
    assert scheduled_call.fee == alarm.getAccountBalance(owner) == alarm.getCallFee(call_key)
    assert scheduled_call.abi_signature == client_contract.doIt.encoded_abi_signature == alarm.getCallABISignature(call_key)
    assert scheduled_call.is_cancelled is False
    assert scheduled_call.was_called is True
    assert scheduled_call.was_successful is True
    assert utils.encode_hex(scheduled_call.data_hash) == 'c2575a0e9e593c00f959f8c92f12db2869c3395a3b0502d05e2516446f71f85b'
