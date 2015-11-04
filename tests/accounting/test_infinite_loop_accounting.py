from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


geth_chain_name = "default-test-lower-gas-limit"


deploy_contracts = [
    "Alarm",
    "InfiniteLoop",
]


def test_infinite_loop_protection(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.InfiniteLoop

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)
    deploy_client.send_transaction(to=client_contract._meta.address, value=1000000000)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(deploy_client, txn_hash)

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None
    deploy_client.wait_for_block(alarm.getCallTargetBlock.call(callKey), 300)
    call_txn_hash = alarm.doCall.sendTransaction(callKey)
    call_txn_receipt = wait_for_transaction(deploy_client, call_txn_hash)
    call_txn = deploy_client.get_transaction_by_hash(call_txn_hash)

    assert alarm.checkIfCalled.call(callKey) is True
    assert alarm.checkIfSuccess.call(callKey) is False

    gas_used = int(call_txn_receipt['gasUsed'], 16)
    expected = int(call_txn['gas'], 16)
    assert gas_used == expected
