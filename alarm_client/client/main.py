import functools

import gevent

from .scanning import (
    scan_for_block_requests,
    scan_for_timestamp_requests,
    map_scan_results_to_handlers,
)


def new_block_callback(latest_block_hash, config):
    web3 = config.web3
    block = web3.eth.getBlock(latest_block_hash)
    config.logger.info("New Block: #%s", block['number'])

    # Takes any of the requests found from scanning and maps them to the main
    # request handler function.
    scan_result_handler = functools.partial(
        map_scan_results_to_handlers,
        config,
    )

    # Scan for any block based requests within the window that we are
    # monitoring.
    block_scanner = gevent.spawn(
        scan_for_block_requests,
        config=config,
    )
    block_scanner.link(scan_result_handler)

    # Scan for any block based requests within the window that we are
    # monitoring.
    timestamp_scanner = gevent.spawn(
        scan_for_timestamp_requests,
        config=config,
    )
    timestamp_scanner.link(scan_result_handler)
