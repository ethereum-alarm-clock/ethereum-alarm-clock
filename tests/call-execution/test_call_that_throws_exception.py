from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction, wait_for_block


geth_chain_name = "default-test-lower-gas-limit"

deploy_contracts = [
    "Alarm",
    "Grove",
    "Fails",
]


def test_what_happens_when_call_throws_exception(geth_node, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.Fails

    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    assert client_contract.value.call() is False
    assert alarm.checkIfCalled.call(callKey) is False
    assert alarm.checkIfSuccess.call(callKey) is False

    wait_for_block(rpc_client, alarm.getCallTargetBlock.call(callKey), 300)
    call_txn_hash = alarm.doCall.sendTransaction(callKey)
    wait_for_transaction(alarm._meta.rpc_client, call_txn_hash)

    assert client_contract.value.call() is False
    assert alarm.checkIfCalled.call(callKey) is True
    assert alarm.checkIfSuccess.call(callKey) is False
