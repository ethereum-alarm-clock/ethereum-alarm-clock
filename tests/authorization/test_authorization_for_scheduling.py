from ethereum import utils

from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction


deploy_contracts = [
    "Alarm",
    "AuthorizesOthers",
]


def test_authorizing_other_address(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.AuthorizesOthers
    coinbase = deploy_client.get_coinbase()

    authed_addr = alarm.authorizedAddress()
    unauthed_addr = alarm.unauthorizedAddress()

    deposit_amount = get_max_gas(deploy_client) * deploy_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(coinbase, value=deposit_amount)

    assert alarm.checkAuthorization(coinbase, client_contract._meta.address) is False

    txn_1_hash = alarm.scheduleCall.sendTransaction(
        client_contract._meta.address,
        client_contract.doIt.encoded_abi_signature,
        utils.decode_hex('c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'),
        deploy_client.get_block_number() + 50,
        255,
        0
    )
    wait_for_transaction(deploy_client, txn_1_hash)

    call_key = alarm.getLastCallKey()
    assert call_key is not None
    deploy_client.wait_for_block(alarm.getCallTargetBlock(call_key), 120)
    call_txn_hash = alarm.doCall.sendTransaction(call_key)
    wait_for_transaction(deploy_client, call_txn_hash)

    assert alarm.checkIfCalled(call_key) is True
    assert alarm.checkIfSuccess(call_key) is True
    assert client_contract.calledBy() == unauthed_addr

    wait_for_transaction(deploy_client, client_contract.authorize.sendTransaction(alarm._meta.address))
    assert alarm.checkAuthorization(coinbase, client_contract._meta.address) is True

    txn_2_hash = alarm.scheduleCall.sendTransaction(
        client_contract._meta.address,
        client_contract.doIt.encoded_abi_signature,
        utils.decode_hex('c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'),
        deploy_client.get_block_number() + 50,
        255,
        0
    )
    wait_for_transaction(deploy_client, txn_2_hash)

    assert call_key != alarm.getLastCallKey()
    call_key = alarm.getLastCallKey()
    assert call_key is not None
    deploy_client.wait_for_block(alarm.getCallTargetBlock(call_key), 120)
    call_txn_hash = alarm.doCall.sendTransaction(call_key)
    wait_for_transaction(deploy_client, call_txn_hash)

    assert alarm.checkIfCalled(call_key) is True
    assert alarm.checkIfSuccess(call_key) is True
    assert client_contract.calledBy() == authed_addr
