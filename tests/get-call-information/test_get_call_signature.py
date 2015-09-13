from populus.utils import wait_for_transaction

from ethereum import utils as ethereum_utils


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_get_call_signature(geth_node, geth_coinbase, deployed_contracts):
    alarm = deployed_contracts.Alarm

    txn_hash = alarm.scheduleCall.sendTransaction(
        geth_coinbase,
        'arst',
        ethereum_utils.decode_hex('c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'),
        1000,
        value=12345,
    )
    wait_for_transaction(alarm._meta.rpc_client, txn_hash)

    call_key = alarm.getLastCallKey.call()
    assert call_key

    alarm.getCallSignature.call(call_key) == 'arst'
