def test_cannot_schedule_too_soon(chain, denoms, SchedulerLib):
    scheduler = chain.get_contract('Scheduler')

    scheduler_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleCall(
        targetBlock=scheduler.call().getFirstSchedulableBlock() - 1,
    )
    chain.wait.for_receipt(scheduler_txn_hash)

    schedule_filter = SchedulerLib.pastEvents('CallRejected', {'address': scheduler.address})
    schedule_logs = schedule_filter.get()
    assert len(schedule_logs) == 1
    schedule_log_data = schedule_logs[0]
    reason = schedule_log_data['args']['reason'].replace('\x00', '')
    assert reason == 'TOO_SOON'
