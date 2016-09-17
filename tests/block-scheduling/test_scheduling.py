import pytest


@pytest.fixture()
def scheduler(chain, request_tracker, request_factory):
    block_scheduler = chain.get_contract('BlockScheduler', deploy_args=[
        request_tracker.address,
        request_factory.address,
    ])
    return block_scheduler


def test_scheduling_with_no_args(chain, web3, denoms, scheduler, RequestData, get_txn_request):
    schedule_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleTransaction()
    schedule_txn_receipt = web3.eth.getTransactionReceipt(schedule_txn_hash)

    txn_request = get_txn_request(schedule_txn_hash)
    request_data = RequestData.from_contract(txn_request)

    assert request_data.txnData.toAddress == web3.eth.coinbase
    assert request_data.schedule.windowStart == schedule_txn_receipt['blockNumber'] + 10


def test_scheduling_with_specified_block(chain,
                                         web3,
                                         denoms,
                                         scheduler,
                                         RequestData,
                                         get_txn_request):
    target_block = web3.eth.blockNumber + 100
    schedule_txn_hash = scheduler.transact({
        'value': 10 * denoms.ether,
    }).scheduleTransaction(
        targetBlock=target_block,
    )

    txn_request = get_txn_request(schedule_txn_hash)
    request_data = RequestData.from_contract(txn_request)

    assert request_data.txnData.toAddress == web3.eth.coinbase
    assert request_data.schedule.windowStart == target_block
