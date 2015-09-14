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
          7       20
         /       /
        4       9
       / \     / \
      1   4   8   15
                 /
                13
               /  \
              9    14
    """
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.SpecifyBlock

    anchor_block = rpc_client.get_block_number()

    blocks = (8, 7, 20, 4, 1, 4, 9, 15, 8, 13, 14, 9)

    call_keys = []

    for n in blocks:
        wait_for_transaction(rpc_client, client_contract.scheduleIt.sendTransaction(alarm._meta.address, anchor_block + 100 + n))

        last_call_key = alarm.getLastCallKey.call()
        assert last_call_key is not None

        call_keys.append(last_call_key)

    calls_to_blocks = dict(zip(call_keys, blocks))

    # Test deeply nested sibling.
    first_9_call = call_keys[6]
    assert calls_to_blocks[first_9_call] == 9

    second_9_call = call_keys[-1]
    assert calls_to_blocks[second_9_call] == 9

    assert alarm.getNextCallSibling.call(first_9_call) == second_9_call

    # Test adjacent sibling
    first_4_call = call_keys[3]
    second_4_call = call_keys[5]

    assert calls_to_blocks[first_4_call] == 4
    assert calls_to_blocks[second_4_call] == 4

    assert alarm.getNextCallSibling.call(first_4_call) == second_4_call

    # Test No siblings
    call_for_20 = call_keys[2]
    assert calls_to_blocks[call_for_20] == 20
    assert alarm.getNextCallSibling.call(call_for_20) is None

    assert alarm.getNextCallSibling.call(second_4_call) is None
    assert alarm.getNextCallSibling.call(second_9_call) is None

    call_for_1 = call_keys[4]
    assert calls_to_blocks[call_for_1] == 1
    assert alarm.getNextCallSibling.call(call_for_1) is None
