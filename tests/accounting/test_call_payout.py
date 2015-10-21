from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "PassesUInt",
]


def test_caller_payout(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.PassesUInt

    coinbase = deploy_client.get_coinbase()

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, 3)
    wait_for_transaction(deploy_client, txn_hash)

    assert client_contract.value() == 0

    call_key = alarm.getLastCallKey()
    assert call_key is not None

    assert alarm.getCallPayout(call_key) == 0
    assert alarm.getAccountBalance(coinbase) == 0

    deploy_client.wait_for_block(alarm.getCallTargetBlock(call_key), 120)
    call_txn_hash = alarm.doCall.sendTransaction(call_key)
    wait_for_transaction(deploy_client, call_txn_hash)

    gas_used = alarm.getCallGasUsed(call_key)
    gas_price = alarm.getCallGasPrice(call_key)
    base_gas_price = alarm.getCallBaseGasPrice(call_key)

    scalar = 100 * base_gas_price / (abs(gas_price - base_gas_price) + base_gas_price)
    expected_payout = gas_used * gas_price * scalar * 101 / 10000

    balance = alarm.getAccountBalance(coinbase)
    assert balance == expected_payout
    assert alarm.getCallPayout(call_key) == balance
