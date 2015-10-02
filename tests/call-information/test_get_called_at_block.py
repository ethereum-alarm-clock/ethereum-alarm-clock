from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction, wait_for_block


deploy_contracts = [
    "Alarm",
    "Grove",
    "NoArgs",
]


def test_getting_called_at_block(geth_node, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.NoArgs

    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(rpc_client, txn_hash)

    assert client_contract.value.call() is False

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    assert alarm.getCallGasUsed.call(callKey) == 0

    wait_for_block(rpc_client, alarm.getCallTargetBlock.call(callKey), 120)
    call_txn_hash = alarm.doCall.sendTransaction(callKey)
    wait_for_transaction(rpc_client, call_txn_hash)

    call_txn = rpc_client.get_transaction_by_hash(call_txn_hash)

    assert client_contract.value.call() is True
    assert alarm.getCallCalledAtBlock.call(callKey) == int(call_txn['blockNumber'], 16)
