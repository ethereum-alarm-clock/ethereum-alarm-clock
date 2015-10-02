from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction, wait_for_block


deploy_contracts = [
    "Alarm",
    "Grove",
    "PassesUInt",
]


def test_call_fee(geth_node, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.PassesUInt

    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, 3)
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    assert client_contract.value.call() == 0

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    before_balance = alarm.accountBalances.call(client_contract._meta.address)

    wait_for_block(rpc_client, alarm.getCallTargetBlock.call(callKey), 120)
    call_txn_hash = alarm.doCall.sendTransaction(callKey)
    wait_for_transaction(alarm._meta.rpc_client, call_txn_hash)

    after_balance = alarm.accountBalances.call(client_contract._meta.address)
    fee = alarm.getCallFee.call(callKey)
    payout = alarm.getCallPayout.call(callKey)

    assert after_balance == before_balance - payout - fee
