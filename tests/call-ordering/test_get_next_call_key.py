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

    key_to_block = dict(zip(call_keys, blocks))

    expected_next_blocks = {
        anchor_block + 1000 + 1: anchor_block + 1000 + 1,
        anchor_block + 1000 + 2: anchor_block + 1000 + 4,
        anchor_block + 1000 + 3: anchor_block + 1000 + 4,
        anchor_block + 1000 + 4: anchor_block + 1000 + 4,
        anchor_block + 1000 + 5: anchor_block + 1000 + 5,
        anchor_block + 1000 + 6: anchor_block + 1000 + 6,
        anchor_block + 1000 + 7: anchor_block + 1000 + 7,
        anchor_block + 1000 + 8: anchor_block + 1000 + 8,
        anchor_block + 1000 + 9: anchor_block + 1000 + 9,
        anchor_block + 1000 + 10: anchor_block + 1000 + 11,
        anchor_block + 1000 + 11: anchor_block + 1000 + 11,
        anchor_block + 1000 + 12: anchor_block + 1000 + 13,
        anchor_block + 1000 + 13: anchor_block + 1000 + 13,
        anchor_block + 1000 + 14: anchor_block + 1000 + 15,
        anchor_block + 1000 + 15: anchor_block + 1000 + 15,
        anchor_block + 1000 + 16: anchor_block + 1000 + 0,
    }

    actual_next_blocks = {
        n: key_to_block[alarm.getNextCallKey.call(n)] for n in expected_next_blocks.keys()
    }

    assert actual_next_blocks == expected_next_blocks
    x = 3
