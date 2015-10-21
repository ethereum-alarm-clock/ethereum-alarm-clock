from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "PassesUInt",
]


def test_call_fee(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.PassesUInt

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, 3)
    wait_for_transaction(deploy_client, txn_hash)

    assert client_contract.value() == 0

    call_key = alarm.getLastCallKey()
    assert call_key is not None

    owner = '0xd3cda913deb6f67967b99d67acdfa1712c293601'

    assert alarm.getCallFee(call_key) == 0
    assert alarm.getAccountBalance(owner) == 0

    deploy_client.wait_for_block(alarm.getCallTargetBlock(call_key), 120)
    call_txn_hash = alarm.doCall.sendTransaction(call_key)
    wait_for_transaction(deploy_client, call_txn_hash)

    balance = alarm.getAccountBalance(owner)
    assert balance > 0
    assert alarm.getCallFee(call_key) == balance
