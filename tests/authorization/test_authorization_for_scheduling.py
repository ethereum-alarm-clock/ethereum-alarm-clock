from ethereum import utils

from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction, wait_for_block


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_authorizing_other_address(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.AuthorizesOthers

    authed_addr = alarm.authorizedAddress.call()
    unauthed_addr = alarm.unauthorizedAddress.call()

    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(geth_coinbase, value=deposit_amount)

    assert alarm.checkAuthorization.call(geth_coinbase, client_contract._meta.address) is False

    txn_1_hash = alarm.scheduleCall.sendTransaction(
        client_contract._meta.address,
        client_contract.doIt.encoded_abi_function_signature,
        utils.decode_hex('c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'),
        rpc_client.get_block_number() + 50,
        255,
        0
    )
    wait_for_transaction(rpc_client, txn_1_hash)

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None
    wait_for_block(rpc_client, alarm.getCallTargetBlock.call(callKey), 120)
    call_txn_hash = alarm.doCall.sendTransaction(callKey)
    wait_for_transaction(rpc_client, call_txn_hash)

    assert alarm.checkIfCalled.call(callKey) is True
    assert alarm.checkIfSuccess.call(callKey) is True
    assert client_contract.calledBy.call() == unauthed_addr

    wait_for_transaction(rpc_client, client_contract.authorize.sendTransaction(alarm._meta.address))
    assert alarm.checkAuthorization.call(geth_coinbase, client_contract._meta.address) is True

    txn_2_hash = alarm.scheduleCall.sendTransaction(
        client_contract._meta.address,
        client_contract.doIt.encoded_abi_function_signature,
        utils.decode_hex('c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'),
        rpc_client.get_block_number() + 50,
        255,
        0
    )
    wait_for_transaction(rpc_client, txn_2_hash)

    assert callKey != alarm.getLastCallKey.call()
    callKey = alarm.getLastCallKey.call()
    assert callKey is not None
    wait_for_block(rpc_client, alarm.getCallTargetBlock.call(callKey), 120)
    call_txn_hash = alarm.doCall.sendTransaction(callKey)
    wait_for_transaction(rpc_client, call_txn_hash)

    assert alarm.checkIfCalled.call(callKey) is True
    assert alarm.checkIfSuccess.call(callKey) is True
    assert client_contract.calledBy.call() == authed_addr
