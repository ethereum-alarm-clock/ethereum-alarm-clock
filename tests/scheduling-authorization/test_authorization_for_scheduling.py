from ethereum import utils

from populus.utils import wait_for_transaction


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_authorizing_other_address(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.AuthorizesOthers

    auth_key = alarm.getAuthorizationKey.call(geth_coinbase, client_contract._meta.address)

    assert alarm.accountAuthorizations.call(auth_key) is False
    assert alarm.getLastCallKey.call() is None

    wait_for_transaction(
        rpc_client,
        alarm.scheduleCall(
            client_contract._meta.address,
            client_contract.doIt.encoded_abi_function_signature,
            utils.decode_hex('c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'),
            rpc_client.get_block_number() + 100,
            255,
        )
    )

    assert alarm.getLastCallKey.call() is None

    wait_for_transaction(rpc_client, client_contract.authorize.sendTransaction(alarm._meta.address))

    assert alarm.accountAuthorizations.call(auth_key) is True

    wait_for_transaction(
        rpc_client,
        alarm.scheduleCall(
            client_contract._meta.address,
            client_contract.doIt.encoded_abi_function_signature,
            utils.decode_hex('c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'),
            rpc_client.get_block_number() + 100,
            255,
        )
    )

    call_key = alarm.getLastCallKey.call()
    assert call_key is not None

    assert alarm.getCallScheduledBy.call(call_key) == geth_coinbase
    assert alarm.getCallTargetAddress.call(call_key) == client_contract._meta.address
