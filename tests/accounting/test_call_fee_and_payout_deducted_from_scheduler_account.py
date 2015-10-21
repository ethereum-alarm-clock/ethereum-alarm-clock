from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "PassesUInt",
]


def test_call_fee_and_payout_deducted_from_account_balance(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.PassesUInt

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, 3)
    wait_for_transaction(deploy_client, txn_hash)

    assert client_contract.value() == 0

    call_key = alarm.getLastCallKey()
    assert call_key is not None

    before_balance = alarm.getAccountBalance(client_contract._meta.address)

    deploy_client.wait_for_block(alarm.getCallTargetBlock(call_key), 120)
    call_txn_hash = alarm.doCall.sendTransaction(call_key)
    wait_for_transaction(deploy_client, call_txn_hash)

    after_balance = alarm.getAccountBalance(client_contract._meta.address)
    fee = alarm.getCallFee(call_key)
    payout = alarm.getCallPayout(call_key)

    assert after_balance == before_balance - payout - fee
