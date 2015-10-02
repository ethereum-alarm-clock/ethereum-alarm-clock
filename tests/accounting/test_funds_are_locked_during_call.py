from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction, wait_for_block


deploy_contracts = [
    "Alarm",
    "Grove",
    "WithdrawsDuringCall",
]


def test_funds_are_locked_during_execution(geth_node, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.WithdrawsDuringCall

    wait_for_transaction(rpc_client, client_contract.setAlarm.sendTransaction(alarm._meta.address))

    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction()
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    assert client_contract.wasCalled.call() is False

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    pre_balance = client_contract.getAlarmBalance.call()
    assert pre_balance == deposit_amount

    wait_for_block(rpc_client, alarm.getCallTargetBlock.call(callKey), 120)
    call_txn_hash = alarm.doCall.sendTransaction(callKey)
    wait_for_transaction(alarm._meta.rpc_client, call_txn_hash)

    fee = alarm.getCallFee.call(callKey)
    payout = alarm.getCallPayout.call(callKey)
    withdrawn_amount = client_contract.withdrawAmount.call()

    assert all(v > 0 for v in (fee, payout, withdrawn_amount))

    post_balance = client_contract.getAlarmBalance.call()
    # Sanity check that an underflow error didn't occur
    assert post_balance < pre_balance
    # During the call, the WithdrawsDuringCall contract tries to withdraw it's
    # entire account balance.  This should only leave the max call cost minus
    # fees left in the account.
    assert post_balance == pre_balance - fee - payout - withdrawn_amount

    assert alarm.checkIfCalled.call(callKey) is True
