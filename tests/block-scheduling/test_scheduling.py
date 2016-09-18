import pytest


@pytest.fixture()
def scheduler(chain, request_tracker, request_factory):
    block_scheduler = chain.get_contract('BlockScheduler', deploy_args=[
        request_tracker.address,
        request_factory.address,
    ])
    return block_scheduler


def test_scheduling_with_full_args(chain,
                                   web3,
                                   denoms,
                                   txn_recorder,
                                   scheduler,
                                   RequestData,
                                   get_txn_request):
    window_start = web3.eth.blockNumber + 20
    schedule_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleTransaction(
        txn_recorder.address,
        'this-is-the-call-data',
        255,  # windowSize
        [
            1212121,  # callGas
            123454321,  # callValue
            98765,  # donation
            80008,  # payment
            123,  # requiredStackDepth
            window_start,  # windowStart
        ],
    )
    web3.eth.getTransactionReceipt(schedule_txn_hash)

    txn_request = get_txn_request(schedule_txn_hash)
    request_data = RequestData.from_contract(txn_request)

    assert request_data.txnData.toAddress == txn_recorder.address
    assert request_data.txnData.callData == 'this-is-the-call-data'
    assert request_data.schedule.windowSize == 255
    assert request_data.txnData.callGas == 1212121
    assert request_data.paymentData.donation == 98765
    assert request_data.paymentData.payment == 80008
    assert request_data.txnData.requiredStackDepth == 123
    assert request_data.schedule.windowStart == window_start


def test_scheduling_with_simplified_args(chain,
                                         web3,
                                         denoms,
                                         txn_recorder,
                                         scheduler,
                                         RequestData,
                                         get_txn_request):
    window_start = web3.eth.blockNumber + 20
    schedule_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleTransaction(
        txn_recorder.address,
        'this-is-the-call-data',
        255,  # windowSize
        [
            1212121,  # callGas
            123454321,  # callValue
            window_start,  # windowStart
        ],
    )
    web3.eth.getTransactionReceipt(schedule_txn_hash)

    txn_request = get_txn_request(schedule_txn_hash)
    request_data = RequestData.from_contract(txn_request)

    assert request_data.txnData.toAddress == txn_recorder.address
    assert request_data.txnData.callData == 'this-is-the-call-data'
    assert request_data.schedule.windowSize == 255
    assert request_data.txnData.callGas == 1212121
    assert request_data.schedule.windowStart == window_start
