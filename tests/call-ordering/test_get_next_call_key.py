from populus.utils import wait_for_transaction


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_get_next_call_with_no_duplicate_block_numbers(geth_node, rpc_client, deployed_contracts):
    """
              8
             / \
            /   \
           /     \
          7       11
         /       /  \
        4       9    12
       / \       \
      1   5       10
           \
            6
    """
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.SpecifyBlock

    anchor_block = rpc_client.get_block_number()

    keys_to_block = {}

    blocks = (8, 7, 11, 4, 5, 1, 9, 6, 10, 12)

    for n in blocks:
        wait_for_transaction(rpc_client, client_contract.scheduleIt.sendTransaction(alarm._meta.address, anchor_block + 1000 + n))

        last_call_key = alarm.getLastCallKey.call()
        assert last_call_key is not None

        keys_to_block[last_call_key] = n

    assert False

    actual_next_blocks = [
        alarm.getNextCallKey.call(anchor_block + 1000 + n) for i in range(1, 14)
    ]
