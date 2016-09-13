def test_call_rejected_for_too_low_stack_depth_check(chain, web3, denoms, SchedulerLib):
    scheduler = chain.get_contract('Scheduler')

    minimum_allowed_stack_depth = scheduler.call().getMinimumStackCheck()

    failed_scheduling_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleCall(
        abiSignature='1234',
        callData='',
        requiredStackDepth=minimum_allowed_stack_depth - 1,
        gracePeriod=255,
        callValue=0,
        targetBlock=web3.eth.blockNumber + 300,
        requiredGas=1000000,
        basePayment=12345,
        baseDonation=54321,
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
    assert reason == 'STACK_CHECK_OUT_OF_RANGE'


def test_call_accepted_for_at_minimum_stack_depth_check(chain, web3, denoms,
                                                        get_scheduled_fbc):
    scheduler = chain.get_contract('Scheduler')

    minimum_allowed_stack_depth = scheduler.call().getMinimumStackCheck()

    scheduling_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleCall(
        abiSignature='1234',
        callData='',
        requiredStackDepth=minimum_allowed_stack_depth,
        gracePeriod=255,
        callValue=0,
        targetBlock=web3.eth.blockNumber + 300,
        requiredGas=1000000,
        basePayment=12345,
        baseDonation=54321,
    )
    chain.wait.for_receipt(scheduling_txn_hash)

    fbc = get_scheduled_fbc(scheduling_txn_hash)
    assert fbc.call().requiredStackDepth() == minimum_allowed_stack_depth


def test_call_rejected_for_too_high_stack_depth_check(chain, web3, denoms, SchedulerLib):
    scheduler = chain.get_contract('Scheduler')

    maximum_allowed_stack_depth = scheduler.call().getMaximumStackCheck()

    failed_scheduling_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleCall(
        abiSignature='1234',
        callData='',
        requiredStackDepth=maximum_allowed_stack_depth + 1,
        gracePeriod=255,
        callValue=0,
        targetBlock=web3.eth.blockNumber + 300,
        requiredGas=1000000,
        basePayment=12345,
        baseDonation=54321,
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
    assert reason == 'STACK_CHECK_OUT_OF_RANGE'


def test_call_accepted_for_maximum_stack_depth_check(chain, web3, denoms, get_scheduled_fbc):
    scheduler = chain.get_contract('Scheduler')

    maximum_allowed_stack_depth = scheduler.call().getMaximumStackCheck()

    scheduling_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleCall(
        abiSignature='1234',
        callData='',
        requiredStackDepth=maximum_allowed_stack_depth,
        gracePeriod=255,
        callValue=0,
        targetBlock=web3.eth.blockNumber + 300,
        requiredGas=1000000,
        basePayment=12345,
        baseDonation=54321,
    )
    chain.wait.for_receipt(scheduling_txn_hash)

    fbc = get_scheduled_fbc(scheduling_txn_hash)
    assert fbc.call().requiredStackDepth() == maximum_allowed_stack_depth
