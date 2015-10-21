from ethereum import utils
from populus.utils import wait_for_transaction

from eth_alarm_client.utils import enumerate_upcoming_calls


deploy_contracts = [
    "Alarm",
    "SpecifyBlock",
]


def test_enumerate_upcoming_tree_positions(deploy_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.SpecifyBlock

    anchor_block = deploy_client.get_block_number()

    blocks = (1, 4, 4, 8, 15, 25, 25, 25, 30, 40, 50, 60)

    call_keys = []

    for n in blocks:
        txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, anchor_block + 100 + n)
        wait_for_transaction(deploy_client, txn_hash)

        last_call_key = alarm.getLastCallKey()
        assert last_call_key is not None

        call_keys.append(last_call_key)

    expected_calls = tuple(utils.encode_hex(c) for c in call_keys[1:10])

    actual_calls = tuple(
        utils.encode_hex(c)
        for c in enumerate_upcoming_calls(alarm, anchor_block + 100 + 4)
    )
    assert actual_calls == expected_calls
