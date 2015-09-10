from populus.utils import wait_for_transaction


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


from ethereum import utils as ethereum_utils


def test_get_scheduled_by(geth_node, geth_coinbase, deployed_contracts):
    alarm = deployed_contracts.Alarm

    txn_hash = alarm.scheduleCall.sendTransaction(
        deployed_contracts.NoArgs._meta.address,
        'arst',
        ethereum_utils.decode_hex('c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'),
        1000,
        value=12345,
    )
    wait_for_transaction(alarm._meta.rpc_client, txn_hash)

    call_key = alarm.getLastCallKey.call()
    assert call_key

    alarm.getCallScheduledBy.call(call_key) == geth_coinbase
