from populus.utils import wait_for_transaction


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def get_tree_state(alarm, calls_to_blocks):
    state = set()
    for call_key, block_number in calls_to_blocks.items():
        if call_key is None:
            continue
        left = calls_to_blocks[alarm.getCallLeftChild.call(call_key)]
        right = calls_to_blocks[alarm.getCallRightChild.call(call_key)]
        state.add((block_number, (left, right)))
    return state


def test_node_tree_positions(geth_node, rpc_client, deployed_contracts):
    """
            1
             \
              4
               \
                7
               / \
              /   \
             /     \
            /       \
           6         8
            \         \
             6         10
                      /  \
                     9    10
                      \
                       9
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

    expected_positions = {
        (8, (None, 10)),
        (7, (6, 8)),
        (10, (9, 10)),
        (4, (None, 7)),
        (6, (None, 6)),
        (1, (None, 4)),
        (9, (None, 9)),
        (6, (None, None)),
        (9, (None, None)),
        (10, (None, None))
    }

    actual_positions = get_tree_state(alarm, calls_to_blocks)

    assert expected_positions == actual_positions
