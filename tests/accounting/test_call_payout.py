from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction, wait_for_block


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_caller_payout(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.PassesUInt

    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, 3)
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    assert client_contract.value.call() == 0

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    assert alarm.getCallPayout.call(callKey) == 0
    assert alarm.accountBalances.call(geth_coinbase) == 0

    wait_for_block(rpc_client, alarm.getCallTargetBlock.call(callKey), 120)
    call_txn_hash = alarm.doCall.sendTransaction(callKey)
    wait_for_transaction(alarm._meta.rpc_client, call_txn_hash)

    gas_used = alarm.getCallGasUsed.call(callKey)
    gas_price = alarm.getCallGasPrice.call(callKey)
    base_gas_price = alarm.getCallBaseGasPrice.call(callKey)

    scalar = 100 * base_gas_price / (abs(gas_price - base_gas_price) + base_gas_price)
    expected_payout = gas_used * gas_price * scalar * 101 / 10000

    balance = alarm.accountBalances.call(geth_coinbase)
    assert balance == expected_payout
    assert alarm.getCallPayout.call(callKey) == balance
