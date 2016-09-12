SCHEDULING_COSTS_MIN = 1160000
SCHEDULING_COSTS_MAX = 1160000

DELTA = 10000


def test_cost_of_scheduling_no_args(chain, denoms, get_scheduled_fbc):
    scheduler = chain.get_contract('Scheduler')

    scheduling_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleCall()
    scheduling_txn_receipt = chain.wait.for_receipt(scheduling_txn_hash)

    fbc = get_scheduled_fbc(scheduling_txn_hash)
    assert fbc.address

    gas_actual = scheduling_txn_receipt['gasUsed']
    assert abs(gas_actual - SCHEDULING_COSTS_MIN) < DELTA


def test_cost_of_scheduling_all_args(chain, web3, denoms, get_scheduled_fbc):
    scheduler = chain.get_contract('Scheduler')

    target_block = web3.eth.blockNumber + 300

    scheduling_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleCall(
        contractAddress=web3.eth.coinbase,
        abiSignature='1234',
        callData="",
        requiredStackDepth=1000,
        gracePeriod=255,
        args=[0, target_block, 300000, 12345, 54321],
    )
    scheduling_txn_receipt = chain.wait.for_receipt(scheduling_txn_hash)

    fbc = get_scheduled_fbc(scheduling_txn_hash)
    assert fbc.address

    gas_actual = scheduling_txn_receipt['gasUsed']
    assert abs(gas_actual - SCHEDULING_COSTS_MAX) < DELTA
