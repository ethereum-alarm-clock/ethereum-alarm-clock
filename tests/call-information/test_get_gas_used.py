from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction, wait_for_block


deploy_contracts = [
    "Alarm",
    "NoArgs",
]


def mine_for_block(evm, block_number):
    while evm.block.number < block_number:
        evm.mine()


def test_getting_gas_used(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.NoArgs

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(deploy_client, txn_hash)

    assert client_contract.value.call() is False

    call_key = alarm.getLastCallKey.call()
    assert call_key is not None

    assert alarm.getCallGasUsed.call(call_key) == 0

    mine_for_block(deploy_client.evm, alarm.getCallTargetBlock(call_key))
    #wait_for_block(rpc_client, alarm.getCallTargetBlock.call(call_key), 120)
    call_txn_hash = alarm.doCall.sendTransaction(call_key)
    call_txn_receipt = wait_for_transaction(deploy_client, call_txn_hash)

    assert client_contract.value.call() is True
    assert alarm.getCallGasUsed.call(call_key) == int(call_txn_receipt['gasUsed'], 16)
