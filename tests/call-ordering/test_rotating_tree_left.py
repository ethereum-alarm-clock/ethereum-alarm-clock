from populus.utils import (
    wait_for_transaction,
    wait_for_block,
)


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


def test_rotating_tree_left(geth_node, rpc_client, deployed_contracts):
    """
    Before left rotation
    ====================

              8
             / \
            /   \
           /     \
          7       1900
         /       /  \
        4       9    2000
       / \     / \
      1   4   8   15
                 /
                13
               /  \
              9    14

    After left rotation
    ===================

               1900
              /   \
             8     2000
            / \
           /   \
          7     9
         /     / \
        4     8   15
       / \       /
      1   4     13
               /  \
              9    14


    """
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.SpecifyBlock

    anchor_block = rpc_client.get_block_number()

    blocks = (8, 7, 1900, 2000, 4, 1, 4, 9, 15, 8, 13, 14, 9)

    call_keys = []

    for n in blocks:
        wait_for_transaction(rpc_client, client_contract.scheduleIt.sendTransaction(alarm._meta.address, anchor_block + 65 + n))

        last_call_key = alarm.getLastCallKey.call()
        assert last_call_key is not None

        call_keys.append(last_call_key)

    assert len(set(call_keys)) == len(blocks)

    calls_to_blocks = dict(zip(call_keys, blocks))
    calls_to_blocks[None] = None

    initial_state = {
        (1, (None, None)),
        (4, (1, 4)),
        (4, (None, None)),
        (8, (7, 1900)),
        (7, (4, None)),
        (1900, (9, 2000)),
        (2000, (None, None)),
        (9, (8, 15)),
        (8, (None, None)),
        (15, (13, None)),
        (13, (9, 14)),
        (9, (None, None)),
        (14, (None, None)),
    }

    assert get_tree_state(alarm, calls_to_blocks) == initial_state

    wait_for_block(rpc_client, anchor_block + 65 + 16, max_wait=120)

    wait_for_transaction(rpc_client, alarm.rotateTree.sendTransaction())

    expected_state = {
        (1, (None, None)),
        (4, (1, 4)),
        (4, (None, None)),
        (8, (7, 9)),
        (7, (4, None)),
        (1900, (8, 2000)),
        (2000, (None, None)),
        (9, (8, 15)),
        (8, (None, None)),
        (15, (13, None)),
        (13, (9, 14)),
        (9, (None, None)),
        (14, (None, None)),
    }

    assert get_tree_state(alarm, calls_to_blocks) == expected_state
