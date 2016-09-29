def test_request_tracker(chain, web3, request_tracker):
    scheduler_address = web3.eth.coinbase

    values = [
        ('0x0000000000000000000000000000000000000001', 2),
        ('0x0000000000000000000000000000000000000002', 1),
        ('0x0000000000000000000000000000000000000003', 4),
        ('0x0000000000000000000000000000000000000004', 10),
        ('0x0000000000000000000000000000000000000005', 10),
        ('0x0000000000000000000000000000000000000006', 3),
        ('0x0000000000000000000000000000000000000007', 2),
        ('0x0000000000000000000000000000000000000008', 8),
        ('0x0000000000000000000000000000000000000009', 3),
        ('0x0000000000000000000000000000000000000010', 4),
        ('0x0000000000000000000000000000000000000011', 0),
        ('0x0000000000000000000000000000000000000012', 2),
    ]
    window_start_lookup = dict(values)

    expected_order = [
        '0x0000000000000000000000000000000000000011',
        '0x0000000000000000000000000000000000000002',
        '0x0000000000000000000000000000000000000001',
        '0x0000000000000000000000000000000000000007',
        '0x0000000000000000000000000000000000000012',
        '0x0000000000000000000000000000000000000006',
        '0x0000000000000000000000000000000000000009',
        '0x0000000000000000000000000000000000000003',
        '0x0000000000000000000000000000000000000010',
        '0x0000000000000000000000000000000000000008',
        '0x0000000000000000000000000000000000000004',
        '0x0000000000000000000000000000000000000005',
    ]

    for request_address, window_start in values:
        add_txn_hash = request_tracker.transact().addRequest(request_address, window_start)
        chain.wait.for_receipt(add_txn_hash)

    assert request_tracker.call().query(scheduler_address, '>=', 0) == expected_order[0]
    assert request_tracker.call().query(scheduler_address, '<=', 20) == expected_order[-1]

    for idx, request_address in enumerate(expected_order):
        assert request_tracker.call().isKnownRequest(scheduler_address, request_address) is True
        assert request_tracker.call().getWindowStart(scheduler_address, request_address) == window_start_lookup[request_address]

        if idx > 0:
            assert request_tracker.call().getPreviousRequest(scheduler_address, request_address) == expected_order[idx - 1]
        else:
            assert request_tracker.call().getPreviousRequest(scheduler_address, request_address) == '0x0000000000000000000000000000000000000000'

        if idx < len(expected_order) - 1:
            assert request_tracker.call().getNextRequest(scheduler_address, request_address) == expected_order[idx + 1]
        else:
            assert request_tracker.call().getNextRequest(scheduler_address, request_address) == '0x0000000000000000000000000000000000000000'


def test_adding_and_removing(chain, web3, request_tracker):
    scheduler_address = web3.eth.coinbase

    assert request_tracker.call().isKnownRequest(scheduler_address, '0x0000000000000000000000000000000000000001') is False

    add_txn_hash = request_tracker.transact().addRequest('0x0000000000000000000000000000000000000001', 12345)
    chain.wait.for_receipt(add_txn_hash)

    assert request_tracker.call().isKnownRequest(scheduler_address, '0x0000000000000000000000000000000000000001') is True

    remove_txn_hash = request_tracker.transact().removeRequest('0x0000000000000000000000000000000000000001')
    chain.wait.for_receipt(remove_txn_hash)

    assert request_tracker.call().isKnownRequest(scheduler_address, '0x0000000000000000000000000000000000000001') is False
