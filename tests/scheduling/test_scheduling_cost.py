deploy_contracts = [
    "CallLib",
    "Scheduler",
    "TestCallExecution",
]


SCHEDULING_COSTS_MIN = 1100000
SCHEDULING_COSTS_MAX = 1120000


def test_cost_of_scheduling_no_args(deploy_client, deployed_contracts, denoms,
                                    get_call):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    targetBlock = deploy_client.get_block_number() + 255 + 10 + 40

    scheduling_txn_hash = scheduler.scheduleCall(
        value=10 * denoms.ether,
        gas=3000000,
    )
    scheduling_txn = deploy_client.get_transaction_by_hash(scheduling_txn_hash)

    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn_hash)
    call = get_call(scheduling_txn_hash)

    delta = 10000

    gas_actual = int(scheduling_receipt['gasUsed'], 16)
    assert abs(gas_actual - SCHEDULING_COSTS_MIN) < delta


def test_cost_of_scheduling_all_args(deploy_client, deployed_contracts, denoms,
                                     get_call):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    targetBlock = deploy_client.get_block_number() + 255 + 10 + 40

    scheduling_txn_hash = scheduler.scheduleCall(
        client_contract._meta.address,
        client_contract.noop.encoded_abi_signature,
        "",
        1000,
        255,
        [0, targetBlock, 300000, 12345, 54321],
        value=10 * denoms.ether,
        gas=3000000,
    )
    scheduling_txn = deploy_client.get_transaction_by_hash(scheduling_txn_hash)

    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn_hash)
    call = get_call(scheduling_txn_hash)

    delta = 10000

    gas_actual = int(scheduling_receipt['gasUsed'], 16)
    assert abs(gas_actual - SCHEDULING_COSTS_MAX) < delta
