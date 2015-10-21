from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "PassesAddress",
]


def test_executing_scheduled_call_with_address(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.PassesAddress

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    address = '0xc948453368e5ddc7bc00bb52b5809138217a068d'

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, address)
    wait_for_transaction(deploy_client, txn_hash)

    assert client_contract.value() == '0x0000000000000000000000000000000000000000'

    call_key = alarm.getLastCallKey()
    assert call_key is not None
    deploy_client.wait_for_block(alarm.getCallTargetBlock(call_key), 120)
    call_txn_hash = alarm.doCall.sendTransaction(call_key)
    wait_for_transaction(deploy_client, call_txn_hash)

    assert client_contract.value() == address
