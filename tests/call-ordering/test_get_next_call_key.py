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
          7       13
         /       /  \
        4       9    15
       / \       \
      1   5       11
           \
            6
    """
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.SpecifyBlock

    anchor_block = rpc_client.get_block_number()

    call_keys = []

    blocks = [anchor_block + 1000 + n for n in (8, 7, 13, 4, 5, 1, 9, 6, 11, 15)]

    for n in blocks:
        wait_for_transaction(rpc_client, client_contract.scheduleIt.sendTransaction(alarm._meta.address, n))

        last_call_key = alarm.getLastCallKey.call()
        assert last_call_key is not None

        call_keys.append(last_call_key)

    key_to_block = dict(zip(call_keys, [b - 1000 - anchor_block for b in blocks]))
    key_to_block[None] = None

    expected_next_blocks = {
        1: 1,
        2: 4,
        3: 4,
        4: 4,
        5: 5,
        6: 6,
        7: 7,
        8: 8,
        9: 9,
        10: 11,
        11: 11,
        12: 13,
        13: 13,
        14: 15,
        15: 15,
        16: None,
    }

    actual_next_blocks = {
        n: key_to_block[alarm.getNextCallKey.call(n + 1000 + anchor_block)]
        for n in expected_next_blocks.keys()
    }

    assert actual_next_blocks == expected_next_blocks
