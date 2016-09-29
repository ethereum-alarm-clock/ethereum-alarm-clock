import click
import functools
import random
import gevent

from web3 import (
    Web3,
    IPCProvider,
)

from .config import Config


def debug_callback(*args, **kwargs):
    click.echo("IN DEBUG:\nargs: {0}\nkwargs: {1}".format(repr(args), repr(kwargs)))


def new_block_callback(latest_block_hash, config):
    web3 = config.web3
    block = web3.eth.getBlock(latest_block_hash)
    click.echo("New Block: #{0}".format(block['number']))

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


NULL_ADDRESS = '0x0000000000000000000000000000000000000000'


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
            raise click.ClickException(unknown_address_msg)
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
                "- next_request @ {arst}\n"
                "- request @ {txn_request.address}\n"
                "- tracker windowStart:  {expected_window_start}\n"
                "- contract windowStart: {txn_request.windowStart}"
            ).format(
                arst=next_request_address,
                expected_window_start=expected_window_start,
                txn_request=txn_request,
            )
            config.logger.error(window_start_mismatch_msg)
            raise click.ClickException(window_start_mismatch_msg)

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

    click.echo("Scanning Blocks {0}-{1}".format(left_boundary, right_boundary))
    return scan_for_requests(config, left_boundary, right_boundary)


def scan_for_timestamp_requests(config):
    web3 = config.web3

    latest_block = web3.eth.getBlock('latest')
    left_boundary = latest_block['timestamp'] - config.back_scan_seconds
    right_boundary = latest_block['timestamp'] + config.forward_scan_seconds

    click.echo("Scanning Timestamps {0}-{1}".format(left_boundary, right_boundary))
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


def locked_txn_request(fn):
    @functools.wraps(fn)
    def inner(config, txn_request):
        lock_key = 'txn-request:{0}'.format(txn_request.address)

        config.logger.debug("Acquiring lock for: %s", lock_key)
        with config.lock(lock_key):
            config.logger.debug("Acquired lock for: %s", lock_key)
            return fn(config, txn_request)
        config.logger.debug("Released lock for: %s", lock_key)

    return inner


@locked_txn_request
def handle_transaction_request(config, txn_request):
    config.logger.debug("Entering `handle_transaction_request`")

    # Early exit conditions
    # - cancelled
    # - before claim window
    # - in freeze window
    if txn_request.isCancelled:
        config.logger.debug("Ignoring Cancelled Request @ %s", txn_request.address)
        return
    elif txn_request.beforeClaimWindow:
        config.logger.debug(
            "Ignoring Pending Request @ %s.  Currently %s.  Not claimable till %s",
            txn_request.address,
            txn_request.now,
            txn_request.claimWindowStart,
        )
        return
    elif txn_request.inClaimWindow:
        config.logger.debug(
            "Spawning `claim_txn_request` for Request @ %s",
            txn_request.address,
        )
        gevent.spawn(claim_txn_request, config, txn_request)
    elif txn_request.inFreezePeriod:
        config.logger.debug("Ignoring Frozen Request @ %s", txn_request.address)
        return
    elif txn_request.inExecutionWindow:
        config.logger.debug(
            "Spawning `execute_txn_request` for Request @ %s",
            txn_request.address,
        )
        gevent.spawn(execute_txn_request, config, txn_request)
    elif txn_request.afterExecutionWindow:
        config.logger.debug(
            "Spawning `cleanup_txn_request` for Request @ %s",
            txn_request.address,
        )
        gevent.spawn(cleanup_txn_request, config, txn_request)

    config.logger.debug("Exiting `handle_transaction_request`")


@locked_txn_request
def claim_txn_request(config, txn_request):
    config.logger.debug("Entering `claim_txn_request`")

    web3 = config.web3
    wait = config.wait

    if txn_request.isCancelled:
        config.logger.debug(
            "Claim Abort for Request @ %s.  Reason: Cancelled",
            txn_request.address,
        )
        return
    elif not txn_request.inClaimWindow:
        config.logger.debug(
            "Claim Abort for Request @ %s.  Reason: Not in claim window",
            txn_request.address,
        )
        return
    elif txn_request.isClaimed:
        config.logger.debug(
            "Claim Abort for Request @ %s.  Reason: already claimed by: %s",
            txn_request.address,
            txn_request.claimedBy,
        )
        return

    payment_if_claimed = (
        txn_request.payment *
        txn_request.paymentModifier *
        txn_request.claimPaymentModifier
    ) // 100 // 100
    claim_deposit = 2 * txn_request.payment
    gas_to_claim = txn_request.estimateGas({'value': claim_deposit}).claim()
    gas_cost_to_claim = web3.eth.gasPrice * gas_to_claim

    if gas_cost_to_claim > payment_if_claimed:
        config.logger.debug(
            "Waiting to claim request @ %s.  Claim gas cost greater than "
            "payment. Claim Gas: %s | Current Payment: %s",
            txn_request.address,
            gas_cost_to_claim,
            payment_if_claimed,
        )
        return

    claim_dice_roll = random.random() * 100
    if claim_dice_roll >= txn_request.claimPaymentModifier:
        config.logger.debug(
            "Waiting to claim request @ %s.  Rolled %s.  Needed at least %s",
            txn_request.address,
            claim_dice_roll,
            txn_request.claimPaymentModifier,
        )

    config.logger.info(
        "Attempting to claim request @ %s.  Payment: %s | PaymentModifier: %s | "
        "Gas Cost %s | Projected Profit: %s",
        txn_request.address,
        payment_if_claimed,
        txn_request.claimPaymentModifier,
        gas_cost_to_claim,
        payment_if_claimed - gas_cost_to_claim,
    )
    claim_txn_hash = txn_request.transact({'value': claim_deposit}).claim()
    config.logger.info(
        "Sent claim transaction for request @ %s.  Txn Hash: %s",
        txn_request.address,
        claim_txn_hash,
    )
    try:
        wait.for_receipt(claim_txn_hash)
    except gevent.Timeout:
        config.logger.error(
            "Timed out waiting for claim transaction receipt for request @ %s. "
            "Txn Hash: %s",
            txn_request.address,
            claim_txn_hash,
        )
        return

    if not txn_request.isClaimed:
        config.logger.error(
            "Request @ %s unexpectedly unclaimed.",
            txn_request.address,
        )
    elif not txn_request.isClaimedBy(web3.eth.defaultAccount):
        config.logger.error(
            "Request @ %s got claimed by %s",
            txn_request.address,
            txn_request.claimedBy,
        )
    else:
        config.logger.info(
            "Successfully claimed request @ %s",
            txn_request.address,
        )

    click.echo("Claiming Request @ {0}".format(txn_request.address))


@locked_txn_request
def execute_txn_request(config, txn_request):
    web3 = config.web3

    if txn_request.wasCalled:
        config.logger.debug(
            "Ignoring Already Executed Request @ %s",
            txn_request.address,
        )
        return

    if txn_request.inReservedWindow:
        if txn_request.isClaimedBy(web3.eth.defaultAccount):
            # todo. implement acquiring a lock here.
            assert False
            # todo: compute required transaction gas.
            execute_txn_hash = txn_request.transact({'gas': 1}).execute()
        else:
            config.logger.debug(
                "Ignoring Request claimed by other @ %s",
                txn_request.address,
            )
            return


@locked_txn_request
def cleanup_txn_request(config, txn_request):
    pass


@click.group()
@click.option(
    '--tracker-address',
    '-t',
)
@click.option(
    '--factory-address',
    '-f',
)
@click.option(
    '--scheduler-address',
    '-s',
)
@click.option(
    '--log-level',
    '-l',
)
@click.option(
    '--provider',
    '-p',
    type=click.Choice(['ipc']),
    default='ipc',
)
@click.option(
    '--ipc-path',
    '-i',
    # TODO: remove this
    default='/Users/piper/sites/ethereum-alarm-clock/chains/local/geth.ipc',
)
@click.pass_context
def main(ctx,
         tracker_address,
         factory_address,
         scheduler_address,
         log_level,
         provider,
         ipc_path):
    if provider == 'ipc':
        web3 = Web3(IPCProvider(ipc_path=ipc_path))
    else:
        raise click.ClickException("This shouldn't be possible")

    config = Config(web3)

    ctx.web3 = web3
    ctx.config = config


VALIDATION_ERRORS = (
    'InsufficientEndowment',
    'ReservedWindowBiggerThanExecutionWindow',
    'InvalidTemporalUnit',
    'ExecutionWindowTooSoon',
    'InvalidRequiredStackDepth',
    'CallGasTooHigh',
    'EmptyToAddress',
)


@main.command('request:create')
@click.option(
    '--to-address',
    '-a',
    default='0x199a239ec2f7c788ce324d28be96fab34f3577f7',
)
@click.option(
    '--call-data',
    '-d',
    default='this-is-test-call-data',
)
@click.option(
    '--call-gas',
    '-g',
    default=150000,
)
@click.option(
    '--call-value',
    '-v',
    default=0,
)
@click.option(
    '--temporal-unit',
    '-t',
    type=click.Choice([1, 2]),
    default=1,
)
@click.option(
    '--window-start',
    '-w',
    type=click.IntRange(min=0),
)
@click.option(
    '--window-size',
    '-w',
    type=click.IntRange(min=0),
    default=255,
)
@click.option(
    '--endowment',
    '-e',
    type=click.IntRange(min=0),
)
@click.option(
    '--confirm/--no-confirm',
    default=True,
)
@click.pass_context
def request_create(ctx,
                   to_address,
                   call_data,
                   call_gas,
                   call_value,
                   temporal_unit,
                   window_start,
                   window_size,
                   endowment,
                   confirm):
    main_ctx = ctx.parent
    config = main_ctx.config

    factory = config.factory
    request_lib = config.request_lib
    payment_lib = config.payment_lib

    pending_request = factory.construct_pending_request(
        temporalUnit=temporal_unit,
        toAddress=to_address,
        callData=call_data,
        callGas=call_gas,
        callValue=call_value,
        windowStart=window_start,
        windowSize=window_size,
    )

    if endowment is None:
        gas_overhead = request_lib.call().EXECUTION_GAS_OVERHEAD()
        endowment = payment_lib.call().computeEndowment(
            payment=pending_request.payment,
            donation=pending_request.donation,
            callGas=pending_request.callGas,
            callValue=pending_request.callValue,
            requiredStackDepth=pending_request.requiredStackDepth,
            gasOverhead=gas_overhead,
        )

    factory_init_kwargs = pending_request.to_init_kwargs()

    validation_checks = factory.call().validateRequestParams(
        endowment=endowment,
        **factory_init_kwargs
    )
    if not all(validation_checks):
        errors = [
            VALIDATION_ERRORS[idx]
            for idx, is_valid in enumerate(validation_checks)
            if is_valid is False
        ]
        validation_error_message = (
            "Invalid Transaction Request Parameters:\n"
            "{0}".format('\n'.join([
                '- {error}'.format(error=error) for error in errors
            ]))
        )
        raise click.ClickException(validation_error_message)

    pre_create_message = '\n'.join((
        "Creating new Transaction Request:",
        pending_request.get_props_display(),
    ))
    click.echo(pre_create_message)
    if confirm:
        if not click.confirm("\n\nContinue with creation?", default=True):
            raise click.ClickException("Cancelled")

    create_txn_hash = factory.transact({
        'value': endowment,
    }).createValidatedRequest(**factory_init_kwargs)

    transaction_sent_message = (
        "\n\n"
        "Sent transaction to create new TransactionRequest:\n"
        " - RequestFactory @ {factory.address}\n"
        " - Txn Hash: {txn_hash}\n\n"
    ).format(factory=factory, txn_hash=create_txn_hash)
    click.echo(transaction_sent_message)

    while True:
        try:
            click.echo("Waiting for transaction to be mined...", nl=False)
            create_txn_receipt = config.wait.for_receipt(create_txn_hash)
            click.echo("MINED via block #{0}".format(
                create_txn_receipt['blockNumber']
            ))
            break
        except gevent.Timeout:
            if confirm:
                wait_longer_msg = (
                    "\n\nTimed out waiting for transaction receipt.  Would you like "
                    "to continue waiting?"
                )
                if click.confirm(wait_longer_msg, default=True):
                    continue
            raise click.ClickException(
                "Timed out waiting for transaction to be mined"
            )

    request_created_filter = factory.pastEvents('RequestCreated', {
        'fromBlock': create_txn_receipt['blockNumber'],
        'toBlock': create_txn_receipt['blockNumber'],
    })
    raw_request_created_logs = request_created_filter.get(False)
    request_created_logs = [
        log_entry for log_entry in raw_request_created_logs
        if log_entry['transactionHash'] == create_txn_hash
    ]

    if len(request_created_logs) == 1:
        txn_request_address = request_created_logs[0]['args']['request']
    else:
        not_found_message = (
            "Unable to find any newly created TransactionRequest contracts."
        )
        if create_txn_receipt['logs']:
            not_found_message += (
                "\nThe following log entries were found:\n{0}"
            ).format('\n'.join([
                '- topics: {0}\n  data: {1}'.format(
                    ', '.join(log_entry['topics']), log_entry['data'],
                ) for log_entry in create_txn_receipt['logs']
            ]))
        raise click.ClickException(not_found_message)

    success_message = (
        "\n\nSuccessfully created new TransactionRequest @ {0}".format(
            txn_request_address,
        )
    )
    click.echo(success_message)


@main.command()
@click.pass_context
def client(ctx):
    main_ctx = ctx.parent
    web3 = main_ctx.web3
    config = main_ctx.config

    new_block_filter = web3.eth.filter('latest')

    click.echo("Starting client")

    callback = functools.partial(new_block_callback, config=config)

    new_block_filter.watch(callback)

    # give it a moment to spin up.
    gevent.sleep(1)

    try:
        while new_block_filter.running is True:
            gevent.sleep(random.random())
    finally:
        if new_block_filter.running:
            click.echo("Stopping Client")
            new_block_filter.stop_watching()


@main.command()
@click.pass_context
def repl(ctx):
    main_ctx = ctx.parent
    web3 = main_ctx.web3
    config = main_ctx.config

    tracker = config.tracker
    factory = config.factory

    import pdb; pdb.set_trace()
