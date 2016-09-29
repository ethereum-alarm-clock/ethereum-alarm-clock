import functools

import gevent

from ..utils import task

from .scanning import (
    scan_for_block_requests,
    scan_for_timestamp_requests,
    map_scan_results_to_handlers,
)
from ..constants import ABORTED_REASON_MAP


@task
def new_block_callback(config, latest_block_hash):
    web3 = config.web3
    logger = config.get_logger('client.blocks')

    block = web3.eth.getBlock(latest_block_hash)
    logger.info("New Block: #%s", block['number'])

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


@task
def executed_event_callback(config, log_entry):
    logger = config.get_logger('client.executed')
    web3 = config.web3
    wait = config.wait
    factory = config.factory

    execute_txn_hash = log_entry['transactionHash']
    execute_txn = web3.eth.getTransaction(execute_txn_hash)
    execute_txn_receipt = wait.for_receipt(execute_txn_hash)

    if not factory.call().isKnownRequest(log_entry['address']):
        logger.info(
            'Executed event from unknown address: %s',
            execute_txn['address'],
        )
        return

    with config.lock(log_entry['address']):
        txn_request = config.get_transaction_request(log_entry['address'])
        txn_request_logger = config.get_logger(txn_request.address)

        logger.info(
            "Request: %s Executed By: %s | Payment: %s | Donation: %s | DonationBenefactor: %s | GasReimbursed: %s | ActualGas: %s",
            txn_request.address,
            execute_txn['from'],
            log_entry['args']['payment'],
            log_entry['args']['donation'],
            txn_request.donationBenefactor,
            log_entry['args']['measuredGasConsumption'],
            execute_txn_receipt['gasUsed'],
        )
        txn_request_logger.info(
            "Executed By: %s | Payment: %s | Donation: %s | DonationBenefactor: %s | GasReimbursed: %s | ActualGas: %s",
            execute_txn['from'],
            log_entry['args']['payment'],
            log_entry['args']['donation'],
            txn_request.donationBenefactor,
            log_entry['args']['measuredGasConsumption'],
            execute_txn_receipt['gasUsed'],
        )


@task
def aborted_event_callback(config, log_entry):
    logger = config.get_logger('client.aborted')
    web3 = config.web3
    factory = config.factory

    aborted_txn_hash = log_entry['transactionHash']
    aborted_txn = web3.eth.getTransaction(aborted_txn_hash)

    if not factory.call().isKnownRequest(log_entry['address']):
        logger.info(
            'Aborted event from unknown address: %s',
            aborted_txn['address'],
        )
        return

    with config.lock(log_entry['address']):
        txn_request = config.get_transaction_request(log_entry['address'])
        txn_request_logger = config.get_logger(txn_request.address)

        logger.info(
            "Found Abort log for Request @ %s. From: %s "
            "| Reason: %s",
            txn_request.address,
            aborted_txn['from'],
            ABORTED_REASON_MAP.get(
                log_entry['args']['reason'],
                'Unknown Errror',
            ),
        )
        txn_request_logger.info(
            "Txn From: %s | Reason: %s",
            aborted_txn['from'],
            ABORTED_REASON_MAP.get(
                log_entry['args']['reason'],
                'Unknown Errror',
            ),
        )
