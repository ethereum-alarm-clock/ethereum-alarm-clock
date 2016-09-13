def test_call_accepted_with_minimum_gas_value(chain, denoms, web3,
                                              SchedulerLib, get_scheduled_fbc):
    scheduler = chain.get_contract('Scheduler')

    target_block = web3.eth.blockNumber + 300

    minimum_gas = scheduler.call().getMinimumCallGas()

    scheduling_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleCall(
        abiSignature='1234',
        targetBlock=target_block,
        requiredGas=minimum_gas,
    )
    chain.wait.for_receipt(scheduling_txn_hash)

    fbc = get_scheduled_fbc(scheduling_txn_hash)
    assert fbc.call().requiredGas() == minimum_gas


def test_call_rejected_below_minimum_gas_value(chain, denoms, web3, SchedulerLib):
    scheduler = chain.get_contract('Scheduler')

    target_block = web3.eth.blockNumber + 300

    minimum_gas = scheduler.call().getMinimumCallGas()

    failed_scheduling_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleCall(
        abiSignature='1234',
        targetBlock=target_block,
        requiredGas=minimum_gas - 1,
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
    assert reason == 'REQUIRED_GAS_OUT_OF_RANGE'


def test_call_accepted_at_maximum_gas(chain, denoms, web3, SchedulerLib, get_scheduled_fbc):
    scheduler = chain.get_contract('Scheduler')

    target_block = web3.eth.blockNumber + 300

    max_allowed_gas = scheduler.call().getMaximumCallGas()

    scheduling_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleCall(
        abiSignature='1234',
        targetBlock=target_block,
        requiredGas=max_allowed_gas,
    )
    chain.wait.for_receipt(scheduling_txn_hash)

    fbc = get_scheduled_fbc(scheduling_txn_hash)
    assert fbc.call().requiredGas() == max_allowed_gas


def test_call_rejected_above_maximum_gas(chain, denoms, web3, SchedulerLib):
    scheduler = chain.get_contract('Scheduler')

    target_block = web3.eth.blockNumber + 300

    max_allowed_gas = scheduler.call().getMaximumCallGas()

    failed_scheduling_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleCall(
        abiSignature='1234',
        targetBlock=target_block,
        requiredGas=max_allowed_gas + 1,
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
    assert reason == 'REQUIRED_GAS_OUT_OF_RANGE'
