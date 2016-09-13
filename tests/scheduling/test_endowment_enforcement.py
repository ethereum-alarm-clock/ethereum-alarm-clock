def test_call_rejected_for_insufficient_endowment(chain, web3, denoms, SchedulerLib):
    scheduler = chain.get_contract('Scheduler')

    target_block = web3.eth.blockNumber + 300

    payment = scheduler.call().defaultPayment()
    donation = scheduler.call().getDefaultDonation()

    required_gas = 1234567

    call_value = 5 * denoms.ether

    # 1 wei short
    endowment = (
        call_value +
        2 * (payment + donation) +
        required_gas * web3.eth.gasPrice
    ) - 1
    required_endowment = scheduler.call().getMinimumEndowment(
        basePayment=payment,
        baseDonation=donation,
        callValue=call_value,
        requiredGas=required_gas,
    )

    assert endowment == required_endowment - 1

    failed_scheduling_txn_hash = scheduler.transact({
        'value': endowment,
    }).scheduleCall(
        abiSignature="1234",
        callData="",
        requiredStackDepth=10,
        gracePeriod=255,
        callValue=call_value,
        targetBlock=target_block,
        requiredGas=required_gas,
        basePayment=payment,
        baseDonation=donation,
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
    assert reason == 'INSUFFICIENT_FUNDS'


def test_call_accepted_for_sufficient_endowment(chain,
                                                web3,
                                                denoms,
                                                SchedulerLib,
                                                get_scheduled_fbc):
    scheduler = chain.get_contract('Scheduler')

    target_block = web3.eth.blockNumber + 300

    payment = scheduler.call().defaultPayment()
    donation = scheduler.call().getDefaultDonation()

    required_gas = 1234567

    call_value = 5 * denoms.ether

    # 1 wei short
    endowment = (
        call_value +
        2 * (payment + donation) +
        required_gas * web3.eth.gasPrice
    )
    required_endowment = scheduler.call().getMinimumEndowment(
        basePayment=payment,
        baseDonation=donation,
        callValue=call_value,
        requiredGas=required_gas,
    )

    assert endowment == required_endowment

    scheduling_txn_hash = scheduler.transact({
        'value': endowment,
    }).scheduleCall(
        abiSignature="1234",
        callData="",
        requiredStackDepth=10,
        gracePeriod=255,
        callValue=call_value,
        targetBlock=target_block,
        requiredGas=required_gas,
        basePayment=payment,
        baseDonation=donation,
    )
    scheduling_txn_receipt = chain.wait.for_receipt(scheduling_txn_hash)

    schedule_filter = SchedulerLib.pastEvents('CallRejected', {
        'address': scheduler.address,
        'fromBlock': scheduling_txn_receipt['blockNumber'],
        'toBlock': scheduling_txn_receipt['blockNumber'],
    })
    schedule_logs = schedule_filter.get()
    assert len(schedule_logs) == 0

    fbc = get_scheduled_fbc(scheduling_txn_hash)
    assert fbc.call().callValue() == call_value
    assert fbc.call().basePayment() == payment
    assert fbc.call().baseDonation() == donation
    assert fbc.call().requiredGas() == required_gas
