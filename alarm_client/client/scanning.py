import gevent

from ..exceptions import InvariantError
from ..constants import NULL_ADDRESS

from .handlers import (
    handle_transaction_request,
)


def scan_for_requests(config, left_boundary, right_boundary):
    config.logger.debug("Entering `scan_for_requests`")

    tracker = config.tracker
    factory = config.factory

    config.logger.debug("Scanning Tracker @ %s", tracker.address)
    config.logger.debug(
        "Validating Tracker results using Factory @ %s",
        factory.address,
    )
    config.logger.debug("Scanning from: %s-%s", left_boundary, right_boundary)

    next_request_address = tracker.call().query(
        factory.address,
        ">=",
        left_boundary,
    )

    config.logger.debug("Initial Tracker Result: %s", next_request_address)

    while next_request_address != NULL_ADDRESS:
        config.logger.debug(
            "Checking Transaction Request @ %s",
            next_request_address,
        )
        if not factory.call().isKnownRequest(next_request_address):
            unknown_address_msg = (
                "Encountered unknown request:\n"
                "- factory: {factory.address}\n"
                "- query: '>='\n"
                "- value: {left_boundary}\n"
                "- request address: {next_request_address}"
            ).format(
                factory=factory,
                left_boundary=left_boundary,
                next_request_address=next_request_address,
            )
            config.logger.error(unknown_address_msg)
            raise InvariantError(unknown_address_msg)
        expected_window_start = tracker.call().getWindowStart(
            factory.address,
            next_request_address,
        )
        txn_request = config.get_transaction_request(next_request_address)
        if txn_request.windowStart != expected_window_start:
            window_start_mismatch_msg = (
                "Encountered tracked request with windowStart value that does "
                "not match windowStart on the actual TransactionRequest "
                "contract:\n"
                "- request @ {txn_request.address}\n"
                "- tracker windowStart:  {expected_window_start}\n"
                "- contract windowStart: {txn_request.windowStart}"
            ).format(
                expected_window_start=expected_window_start,
                txn_request=txn_request,
            )
            config.logger.error(window_start_mismatch_msg)
            InvariantError(window_start_mismatch_msg)

        if txn_request.windowStart <= right_boundary:
            config.logger.debug(
                "Found Request @ %s - windowStart: %s",
                txn_request.address,
                txn_request.windowStart,
            )
            yield txn_request
        else:
            config.logger.debug(
                "Scan Exit Condition: windowStart: %s > right_boundary: %s",
                txn_request.windowStart,
                right_boundary,
            )
            break

        next_request_address = tracker.call().getNextRequest(
            factory.address,
            txn_request.address,
        )

    config.logger.debug("Exiting `scan_for_requests`")


def scan_for_block_requests(config):
    web3 = config.web3

    left_boundary = web3.eth.blockNumber - config.back_scan_blocks
    right_boundary = web3.eth.blockNumber + config.forward_scan_blocks

    config.logger.debug("Scanning Blocks %s-%s", left_boundary, right_boundary)
    return scan_for_requests(config, left_boundary, right_boundary)


def scan_for_timestamp_requests(config):
    web3 = config.web3

    latest_block = web3.eth.getBlock('latest')
    left_boundary = latest_block['timestamp'] - config.back_scan_seconds
    right_boundary = latest_block['timestamp'] + config.forward_scan_seconds

    config.logger.debug("Scanning Timestamps %s-%s", left_boundary, right_boundary)
    return scan_for_requests(config, left_boundary, right_boundary)


def map_scan_results_to_handlers(config, scan_greenlet):
    config.logger.debug("Entering `map_scan_results_to_handlers`")
    if scan_greenlet.successful():
        for txn_request in scan_greenlet.value:
            config.logger.debug(
                "Spawning handler for txn_request @ %s",
                txn_request.address,
            )
            gevent.spawn(
                handle_transaction_request,
                config=config,
                txn_request=txn_request,
            )
    else:
        config.logger.error(str(scan_greenlet.exception))
    config.logger.debug("Exiting `map_scan_results_to_handlers`")
