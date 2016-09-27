import pytest


@pytest.fixture()
def scheduler(chain, web3, request_tracker, request_factory):
    block_scheduler = chain.get_contract('BlockScheduler', deploy_args=[
        request_tracker.address,
        request_factory.address,
    ])
    chain_code = web3.eth.getCode(block_scheduler.address)
    assert len(chain_code) > 10
    return block_scheduler


def test_block_scheduling_with_full_args(chain,
                                         web3,
                                         denoms,
                                         txn_recorder,
                                         scheduler,
                                         request_factory,
                                         request_tracker,
                                         RequestData,
                                         get_txn_request):
    window_start = web3.eth.blockNumber + 20
    schedule_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleTransaction(
        txn_recorder.address,
        'this-is-the-call-data',
        [
            1212121,  # callGas
            123454321,  # callValue
            98765,  # donation
            80008,  # payment
            123,  # requiredStackDepth
            54321,  # windowSize
            window_start,  # windowStart
        ],
    )
    schedule_txn_receipt = web3.eth.getTransactionReceipt(schedule_txn_hash)

    assert schedule_txn_receipt['gasUsed'] < 1300000

    txn_request = get_txn_request(schedule_txn_hash)
    request_data = RequestData.from_contract(txn_request)

    assert request_data.txnData.toAddress == txn_recorder.address
    assert request_data.txnData.callData == 'this-is-the-call-data'
    assert request_data.schedule.windowSize == 54321
    assert request_data.txnData.callGas == 1212121
    assert request_data.paymentData.donation == 98765
    assert request_data.paymentData.payment == 80008
    assert request_data.txnData.requiredStackDepth == 123
    assert request_data.schedule.windowStart == window_start


def test_block_scheduling_with_simplified_args(chain,
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
        [
            1212121,  # callGas
            123454321,  # callValue
            255,  # windowSize
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


def test_invalid_schedule_returns_ether(chain,
                                        web3,
                                        denoms,
                                        txn_recorder,
                                        scheduler,
                                        RequestData,
                                        get_txn_request):
    latest_block = web3.eth.getBlock('latest')
    window_start = web3.eth.blockNumber + 20

    before_balance = web3.eth.getBalance(web3.eth.accounts[1])

    schedule_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
        'from': web3.eth.accounts[1],
    }).scheduleTransaction(
        txn_recorder.address,
        'this-is-the-call-data',
        [
            latest_block['gasLimit'],  # callGas - too high a value.
            123454321,  # callValue
            0,  # windowSize
            window_start,  # windowStart
        ],
    )
    schedule_txn_receipt = web3.eth.getTransactionReceipt(schedule_txn_hash)

    after_balance = web3.eth.getBalance(web3.eth.accounts[1])
    assert before_balance - after_balance <= denoms.ether
    assert before_balance - after_balance == schedule_txn_receipt['gasUsed'] * web3.eth.gasPrice

    with pytest.raises(AssertionError):
        get_txn_request(schedule_txn_hash)
