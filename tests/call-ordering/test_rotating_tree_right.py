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


def test_rotating_tree_right(geth_node, rpc_client, deployed_contracts):
    """
    Before right rotation
    ====================

         1
          \
           15
          /  \
         4    \
        / \    \
       3   7    \
                 1800
                /    \
               /      \
             1700      2000
                      /    \
                     /      \
                    /        \
                   1900       2001


    After right rotation
    ====================

               15
              /  \
             /    \
            /      \
           1        1800
            \      /  \
             4    /    \
            / \  1700   2000
           3   7       /  \
                     1900  2001


    """
    initial_state = {
        (2001, (None, None)),
        (1900, (None, None)),
        (1700, (None, None)),
        (4, (3, 7)),
        (3, (None, None)),
        (7, (None, None)),
        (1, (None, 15)),
        (15, (4, 1800)),
        (1800, (1700, 2000)),
        (2000, (1900, 2001)),
    }
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.SpecifyBlock

    anchor_block = rpc_client.get_block_number()

    blocks = (2000, 1800, 2001, 15, 1700, 1900, 1, 4, 3, 7)

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
        (2001, (None, None)),
        (1900, (None, None)),
        (1700, (None, None)),
        (4, (3, 7)),
        (3, (None, None)),
        (7, (None, None)),
        (1, (None, 15)),
        (15, (4, 1800)),
        (1800, (1700, 2000)),
        (2000, (1900, 2001)),
    }

    assert get_tree_state(alarm, calls_to_blocks) == initial_state

    wait_for_block(rpc_client, anchor_block + 65 + 16, max_wait=180)

    wait_for_transaction(rpc_client, alarm.rotateTree.sendTransaction())

    expected_state = {
        (1700, (None, None)),
        (2001, (None, None)),
        (3, (None, None)),
        (1, (None, 4)),
        (4, (3, 7)),
        (15, (1, 1800)),
        (2000, (1900, 2001)),
        (1900, (None, None)),
        (7, (None, None)),
        (1800, (1700, 2000)),
    }

    assert get_tree_state(alarm, calls_to_blocks) == expected_state
