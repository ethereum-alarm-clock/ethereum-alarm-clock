import bisect

from alarm_client.utils import (
    find_block_left_of_timestamp,
    find_block_right_of_timestamp,
)


def test_finding_block_left_of_timestamp(chain, web3, set_timestamp):
    chain.wait.for_block(1)
    base_block = web3.eth.getBlock('latest')

    base_timestamp = base_block['timestamp']

    timestamps = [
        base_timestamp,
        base_timestamp + 10,
        base_timestamp + 10 + 5,
        base_timestamp + 10 + 5 + 20,
        base_timestamp + 10 + 5 + 20 + 10,
        base_timestamp + 10 + 5 + 20 + 10 + 10,
    ]

    for timestamp in timestamps[1:]:
        set_timestamp(timestamp)

    blocks = [
        web3.eth.getBlock(i)
        for i in range(base_block['number'], base_block['number'] + 6)
    ]
    assert len(blocks) == len(timestamps)
    for block, timestamp in zip(blocks, timestamps):
        assert block['timestamp'] == timestamp

    earliest_block = web3.eth.getBlock(1)
    latest_block = web3.eth.getBlock('latest')

    expected = [
        (i, base_block['number'] + bisect.bisect_right(timestamps, i) - 1)
        for i in range(base_timestamp, timestamps[-1] + 1)
    ]

    for timestamp, expected_block_number in expected:
        if timestamp == earliest_block['timestamp']:
            expected_block_number = 'earliest'
        if timestamp == latest_block['timestamp']:
            expected_block_number = 'latest'
        actual_block_number = find_block_left_of_timestamp(web3, timestamp)
        assert actual_block_number == expected_block_number
        block = web3.eth.getBlock(actual_block_number)
        assert block['timestamp'] <= timestamp


def test_finding_block_right_of_timestamp(chain, web3, set_timestamp):
    chain.wait.for_block(1)
    base_block = web3.eth.getBlock('latest')

    base_timestamp = base_block['timestamp']

    timestamps = [
        base_timestamp,
        base_timestamp + 10,
        base_timestamp + 10 + 5,
        base_timestamp + 10 + 5 + 20,
        base_timestamp + 10 + 5 + 20 + 10,
        base_timestamp + 10 + 5 + 20 + 10 + 10,
    ]

    for timestamp in timestamps[1:]:
        set_timestamp(timestamp)

    blocks = [
        web3.eth.getBlock(i)
        for i in range(base_block['number'], base_block['number'] + 6)
    ]
    assert len(blocks) == len(timestamps)
    for block, timestamp in zip(blocks, timestamps):
        assert block['timestamp'] == timestamp

    earliest_block = web3.eth.getBlock(1)
    latest_block = web3.eth.getBlock('latest')

    expected = [
        (i, base_block['number'] + bisect.bisect_left(timestamps, i))
        for i in range(base_timestamp, timestamps[-1] + 1)
    ]

    for timestamp, expected_block_number in expected:
        if timestamp == earliest_block['timestamp']:
            expected_block_number = 'earliest'
        if timestamp == latest_block['timestamp']:
            expected_block_number = 'latest'
        actual_block_number = find_block_right_of_timestamp(web3, timestamp)
        assert actual_block_number == expected_block_number
        block = web3.eth.getBlock(
            1 if actual_block_number == 'earliest' else actual_block_number
        )
        assert block['timestamp'] >= timestamp
