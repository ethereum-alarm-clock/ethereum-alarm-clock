def test_cannot_schedule_with_too_small_grace_perioud(chain, web3, denoms, SchedulerLib):
    scheduler = chain.get_contract('Scheduler')

    minimum_grace_period = scheduler.call().getMinimumGracePeriod()

    failed_scheduling_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleCall(
        abiSignature='1234',
        targetBlock=web3.eth.blockNumber + 300,
        requiredGas=1000000,
        gracePeriod=minimum_grace_period - 1,
    )
    failed_scheduling_txn_receipt = chain.wait.for_receipt(failed_scheduling_txn_hash)

    schedule_filter = SchedulerLib.pastEvents('CallRejected', {
        'address': scheduler.address,
        'fromBlock': failed_scheduling_txn_receipt['blockNumber'],
        'toBlock': failed_scheduling_txn_receipt['blockNumber'],
    })
    schedule_logs = schedule_filter.get()
    assert len(schedule_logs) == 1
    schedule_log_data = schedule_logs[0]
    reason = schedule_log_data['args']['reason'].replace('\x00', '')
    assert reason == 'GRACE_TOO_SHORT'


def test_schedule_accepted_with_minimum_grace_period(chain, web3, denoms, get_scheduled_fbc):
    scheduler = chain.get_contract('Scheduler')

    minimum_grace_period = scheduler.call().getMinimumGracePeriod()

    scheduling_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleCall(
        abiSignature='1234',
        targetBlock=web3.eth.blockNumber + 300,
        requiredGas=1000000,
        gracePeriod=minimum_grace_period,
    )
    chain.wait.for_receipt(scheduling_txn_hash)

    fbc = get_scheduled_fbc(scheduling_txn_hash)
    assert fbc.call().gracePeriod() == minimum_grace_period
