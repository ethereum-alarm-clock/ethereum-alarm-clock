from ethereum import utils

from eth_alarm_client.utils import enumerate_upcoming_calls


deploy_contracts = [
    "Scheduler",
    "TestCallExecution",
]


def test_enumerate_upcoming_tree_positions(deploy_client, deployed_contracts,
                                           denoms, get_call):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    anchor_block = deploy_client.get_block_number()

    blocks = (1, 4, 4, 8, 15, 25, 25, 25, 30, 40, 50, 60)

    calls = []

    for n in blocks:
        scheduling_txn = scheduler.scheduleCall(
            client_contract._meta.address,
            client_contract.setBool.encoded_abi_signature,
            anchor_block + 100 + n,
            1000000,
            value=10 * denoms.ether,
            gas=3000000,
        )
        scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn)
        call = get_call(scheduling_txn)

        calls.append(call)

    expected_calls = tuple(call._meta.address for call in calls[1:10])
    actual_calls = tuple(
        c for c in enumerate_upcoming_calls(scheduler, anchor_block + 100 + 4)
    )
    assert actual_calls == expected_calls

    expected_calls = tuple(call._meta.address for call in calls[10:])
    actual_calls = tuple(
        c for c in enumerate_upcoming_calls(scheduler, anchor_block + 100 + 41)
    )
    assert actual_calls == expected_calls
