from populus.utils import wait_for_transaction


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_node_tree_positions(geth_node, rpc_client, deployed_contracts):
    """
              8
             / \
            /   \
           /     \
          7       10
         /       /  \
        4       9    10
       / \       \
      1   6       9
           \
            6
    """
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.SpecifyBlock

    anchor_block = rpc_client.get_block_number()

    blocks = (8, 7, 10, 4, 6, 1, 9, 6, 9, 10)

    call_keys = []

    for n in blocks:
        wait_for_transaction(rpc_client, client_contract.scheduleIt.sendTransaction(alarm._meta.address, anchor_block + 100 + n))

        last_call_key = alarm.getLastCallKey.call()
        assert last_call_key is not None

        call_keys.append(last_call_key)

    calls_to_blocks = dict(zip(call_keys, blocks))
    calls_to_blocks[None] = None

    actual_positions = []

    expected_positions = [
        (8, (7, 10)),
        (7, (4, None)),
        (10, (9, 10)),
        (4, (1, 6)),
        (6, (None, 6)),
        (1, (None, None)),
        (9, (None, 9)),
        (6, (None, None)),
        (9, (None, None)),
        (10, (None, None)),
    ]

    for n, callKey in zip(blocks, call_keys):
        left = calls_to_blocks[alarm.getCallLeftChild.call(callKey)]
        right = calls_to_blocks[alarm.getCallRightChild.call(callKey)]
        actual_positions.append((n, (left, right)))

    assert expected_positions == actual_positions
