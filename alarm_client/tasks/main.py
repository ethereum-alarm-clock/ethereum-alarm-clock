import functools

import gevent

from ..utils import task
from ..constants import (
    ABORTED_REASON_MAP,
    VALIDATION_ERRORS,
)
from ..exceptions import InvariantError

from .scanning import (
    scan_for_block_requests,
    scan_for_timestamp_requests,
    map_scan_results_to_handlers,
)


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

    for txn_hash in block['transactions']:
        gevent.spawn(
            mined_transaction_report,
            config=config,
            txn_hash=txn_hash,
        )


@task
def mined_transaction_report(config, txn_hash):
    web3 = config.web3
    factory = config.factory

    txn = web3.eth.getTransaction(txn_hash)

    if txn['from'] != web3.eth.defaultAccount:
        config.get_logger('client.txn_mined').debug(
            'Ignoring transaction.  Not sent by this client'
        )
        return
    if not factory.call().isKnownRequest(txn['to']):
        config.get_logger('client.txn_mined').debug(
            'Ignoring transaction.  Not to a known TransactionRequest contract'
        )
        return

    txn_request = config.get_transaction_request(txn['to'])
    txn_data = txn['input']

    logger = config.get_logger(txn_request.address)

    if txn_data.startswith(txn_request.claim_selector):
        if txn_request.isClaimedBy(web3.eth.defaultAccount):
            logger.info(
                "Successfully claimed request. PaymentModifier: %s",
                txn_request.paymentModifier,
            )
        elif txn_request.isClaimed:
            logger.error(
                "Request got claimed by other: %s",
                txn_request.claimedBy,
            )
        else:
            logger.error(
                "Request should be claimed but isn't.  Tried claiming "
                "via txn: %s",
                txn_hash,
            )
    elif txn_data.startswith(txn_request.execute_selector):
        if txn_request.wasCalled:
            if txn_request.paymentBenefactor == web3.eth.defaultAccount:
                logger.info("Request successfully executed")
            else:
                logger.error(
                    "Request got executed by other: %s",
                    txn_request.paymentBenefactor,
                )
        else:
            logger.error(
                "Request should have been executed but was not.  Tried "
                "execution via txn: %s",
                txn_hash,
            )
    elif txn_data.startswith(txn_request.cancel_selector):
        if txn_request.isCancelled:
            logger.info("Request was cancelled")
        else:
            logger.error(
                "Request should have been cancelled but was not.  Tried "
                "cancelling via txn: %s",
                txn_hash,
            )
    else:
        logger.warning(
            "Unrecognized transaction found.  Txn Hash: %s",
            txn_hash,
        )


@task
def executed_event_callback(config, log_entry):
    logger = config.get_logger('client.request.executed')
    web3 = config.web3
    wait = config.wait
    factory = config.factory

    execute_txn_hash = log_entry['transactionHash']
    execute_txn = web3.eth.getTransaction(execute_txn_hash)
    execute_txn_receipt = wait.for_receipt(execute_txn_hash)

    if not factory.call().isKnownRequest(log_entry['address']):
        logger.info(
            'Executed event from unknown address: %s',
            log_entry['address'],
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
    logger = config.get_logger('client.request.aborted')
    web3 = config.web3
    factory = config.factory

    aborted_txn_hash = log_entry['transactionHash']
    aborted_txn = web3.eth.getTransaction(aborted_txn_hash)

    if not factory.call().isKnownRequest(log_entry['address']):
        logger.info(
            'Aborted event from unknown address: %s',
            log_entry['address'],
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


@task
def cancelled_event_callback(config, log_entry):
    logger = config.get_logger('client.request.cancelled')
    factory = config.factory

    if not factory.call().isKnownRequest(log_entry['address']):
        logger.info(
            'Cancelled event from unknown address: %s',
            log_entry['address'],
        )
        return

    with config.lock(log_entry['address']):
        txn_request = config.get_transaction_request(log_entry['address'])
        txn_request_logger = config.get_logger(txn_request.address)

        logger.info("Cancelled: Request @ %s", txn_request.address)
        txn_request_logger.info("Cancelled")


@task
def claimed_event_callback(config, log_entry):
    logger = config.get_logger('client.request.claimed')
    web3 = config.web3
    wait = config.wait
    factory = config.factory

    claimed_txn_hash = log_entry['transactionHash']
    claimed_txn_receipt = wait.for_receipt(claimed_txn_hash)

    if not factory.call().isKnownRequest(log_entry['address']):
        logger.info(
            'Claimed event from unknown address: %s',
            log_entry['address'],
        )
        return

    with config.lock(log_entry['address']):
        txn_request = config.get_transaction_request(log_entry['address'])
        txn_request_logger = config.get_logger(txn_request.address)

        claimed_at_block = web3.eth.getBlock(claimed_txn_receipt['blockNumber'])

        if txn_request.temporalUnit == 1:
            claimed_at_now = claimed_at_block['number']
        elif txn_request.temporalUnit == 2:
            claimed_at_now = claimed_at_block['timestamp']
        else:
            raise InvariantError(
                "Invalid temporalUnit: {0}".format(txn_request.temporalUnit)
            )

        claim_index = claimed_at_now - txn_request.claimWindowStart

        logger.info(
            "Claimed: Request @ %s: ClaimedBy: %s | ClaimedAt %s %s / %s (%s%%)",
            txn_request.address,
            txn_request.claimedBy,
            "block" if txn_request.temporalUnit == 1 else "second",
            claim_index,
            txn_request.claimWindowSize,
            txn_request.paymentModifier,
        )
        txn_request_logger.info("Claimed: ClaimedBy: %s", txn_request.claimedBy)


@task
def created_event_callback(config, log_entry):
    logger = config.get_logger('client.factory.created')
    wait = config.wait
    factory = config.factory

    create_txn_hash = log_entry['transactionHash']
    wait.for_receipt(create_txn_hash)

    if not factory.call().isKnownRequest(log_entry['args']['request']):
        logger.error(
            'RequestCreated event request is not known by factory: %s',
            log_entry['args']['request'],
        )
        raise InvariantError(
            'RequestCreated event logged by factory @ {0} for request @ {1} but '
            'request is not known by factory'.format(
                log_entry['address'],
                log_entry['args']['request'],
            )
        )

    txn_request = config.get_transaction_request(log_entry['args']['request'])
    txn_request_logger = config.get_logger(txn_request.address)

    logger.info(
        "RequestCreated @ %s\n----------------\n%s",
        txn_request.address,
        txn_request.get_props_display()
    )
    txn_request_logger.info(
        "RequestCreated @ %s\n----------------\n%s",
        txn_request.address,
        txn_request.get_props_display()
    )


@task
def validation_error_event_callback(config, log_entry):
    logger = config.get_logger('client.factory.validation_error')
    wait = config.wait

    create_txn_hash = log_entry['transactionHash']
    wait.for_receipt(create_txn_hash)

    logger.info(
        "ValidationError from factory @ %s\n----------------\nReason: %s",
        log_entry['address'],
        VALIDATION_ERRORS.get(
            log_entry['args']['error'],
            'Unknown Error Code: {0}'.format(log_entry['args']['error'])
        )
    )
