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

    call_keys = []

    for n in (8, 7, 10, 4, 6, 1, 9, 6, 9, 10):
        wait_for_transaction(rpc_client, client_contract.scheduleIt.sendTransaction(alarm._meta.address, anchor_block + 100 + n))

        last_call_key = alarm.getLastCallKey.call()
        assert last_call_key is not None

        call_keys.append(last_call_key)

    expected_positions = (
        'b',
        'bl',
        'br',
        'bll',
        'bllr',
        'blll',
        'brl',
        'bllrr',
        'brlr',
        'brr',
    )

    actual_positions = [
        alarm.getCallTreePosition.call(call_key) for call_key in call_keys
    ]

    for actual_position, expected_position in zip(actual_positions, expected_positions):
        assert actual_position == expected_position
