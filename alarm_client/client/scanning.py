import gevent

from ..exceptions import InvariantError
from ..constants import NULL_ADDRESS
from ..utils import task

from .handlers import (
    handle_transaction_request,
)


@task
def scan_for_requests(config, left_boundary, right_boundary):
    logger = config.get_logger('client.scanner')

    tracker = config.tracker
    factory = config.factory

    logger.debug("Scanning Tracker @ %s", tracker.address)
    logger.debug(
        "Validating Tracker results using Factory @ %s",
        factory.address,
    )
    logger.debug("Scanning from: %s-%s", left_boundary, right_boundary)

    next_request_address = tracker.call().query(
        factory.address,
        ">=",
        left_boundary,
    )

    logger.debug("Initial Tracker Result: %s", next_request_address)

    while next_request_address != NULL_ADDRESS:
        logger.debug("Found Request @ %s", next_request_address)
        if not factory.call().isKnownRequest(next_request_address):
            logger.error(
                "Encountered unknown request: factory: %s | query: '>=' | "
                "value: %s | address: %s",
                factory.address,
                left_boundary,
                next_request_address,
            )
            raise InvariantError(
                "Encountered Unknown address: {0}".format(next_request_address)
            )
        tracker_window_start = tracker.call().getWindowStart(
            factory.address,
            next_request_address,
        )
        txn_request = config.get_transaction_request(next_request_address)
        if txn_request.windowStart != tracker_window_start:
            logger.error(
                "Encountered tracked request with windowStart value that does "
                "not match windowStart on the actual TransactionRequest "
                "contract: request: %s | tracker windowStart: %s | "
                "contractWindowStart: %s",
                txn_request.address,
                tracker_window_start,
                txn_request.windowStart,
            )
            InvariantError(
                "Window start mismatch for request: {0}".format(
                    txn_request.address,
                )
            )

        if txn_request.windowStart <= right_boundary:
            logger.debug(
                "Found Request @ %s - windowStart: %s",
                txn_request.address,
                txn_request.windowStart,
            )
            yield txn_request
        else:
            logger.debug(
                "Scan Exit Condition: windowStart: %s > right_boundary: %s",
                txn_request.windowStart,
                right_boundary,
            )
            break

        next_request_address = tracker.call().getNextRequest(
            factory.address,
            txn_request.address,
        )


@task
def scan_for_block_requests(config):
    logger = config.get_logger('client.scanner.blocks')
    web3 = config.web3

    left_boundary = web3.eth.blockNumber - config.back_scan_blocks
    right_boundary = web3.eth.blockNumber + config.forward_scan_blocks

    logger.debug("Scanning Blocks %s-%s", left_boundary, right_boundary)
    return scan_for_requests(config, left_boundary, right_boundary)


@task
def scan_for_timestamp_requests(config):
    logger = config.get_logger('client.scanner.timestamps')
    web3 = config.web3

    latest_block = web3.eth.getBlock('latest')
    left_boundary = latest_block['timestamp'] - config.back_scan_seconds
    right_boundary = latest_block['timestamp'] + config.forward_scan_seconds

    logger.debug("Scanning Timestamps %s-%s", left_boundary, right_boundary)
    return scan_for_requests(config, left_boundary, right_boundary)


@task
def map_scan_results_to_handlers(config, scan_greenlet):
    logger = config.get_logger('client.scanner.mapper')
    logger.debug("Entering `map_scan_results_to_handlers`")
    if scan_greenlet.successful():
        for txn_request in scan_greenlet.value:
            logger.debug(
                "Spawning handler for txn_request @ %s",
                txn_request.address,
            )
            gevent.spawn(
                handle_transaction_request,
                config=config,
                txn_request=txn_request,
            )
    else:
        logger.error(str(scan_greenlet.exception))
    logger.debug("Exiting `map_scan_results_to_handlers`")
